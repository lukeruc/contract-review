#!/usr/bin/env node
/**
 * safe-docx helper — JSON-RPC wrapper over the safe-docx MCP server.
 *
 * Usage:
 *   node docx-helper.mjs <operation> --flag value [--and <operation> --flag value ...]
 *
 * All operations within one invocation share the same MCP session,
 * so you can read, edit, comment, and save in a single command.
 *
 * Shared flags (apply to all ops unless overridden per-op):
 *   --file <path>     DOCX file to operate on
 *
 * Operations:
 *   read       read_file
 *   grep       search with --pattern
 *   replace    replace_text (needs --para, --old, --new)
 *   comment    add_comment (needs --author, --text; optional --para)
 *   get-comments  get_comments
 *   footnote   add_footnote (needs --para, --text)
 *   save       save (needs --out; optional --mode clean|tracked|both)
 *   compare    compare_documents (needs --original, --revised, --out)
 *
 * Example (full workflow):
 *   node docx-helper.mjs read --file contract.docx \
 *     --and comment --author "Reviewer" --text "Changed per client" --para _bk_xxx \
 *     --and save --out output.docx --mode both
 */

import { spawn } from 'node:child_process';

const MCP_CMD = 'npx';
const MCP_ARGS = ['-y', '@usejunior/safe-docx'];

function parsePipeline() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Usage: node docx-helper.mjs <operation> --flags [--and <operation> --flags ...]');
    process.exit(1);
  }

  const steps = [];
  let current = { op: null, flags: {} };
  let i = 0;

  while (i < args.length) {
    if (args[i] === '--and' || args[i] === '--then') {
      if (current.op) steps.push(current);
      current = { op: null, flags: {} };
      i++;
      continue;
    }
    if (!args[i].startsWith('--') && current.op === null) {
      current.op = args[i];
      i++;
      continue;
    }
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
        current.flags[key] = args[i + 1];
        i += 2;
      } else {
        current.flags[key] = true;
        i++;
      }
      continue;
    }
    // positional arg after op (treat as extra)
    i++;
  }
  if (current.op) steps.push(current);

  // Propagate shared --file from first step to later steps that lack it
  const sharedFile = steps.length > 0 ? (steps[0].flags.file || steps[0].flags['file-path']) : null;
  for (const step of steps) {
    if (!step.flags.file && !step.flags['file-path'] && sharedFile) {
      step.flags.file = sharedFile;
    }
  }

  return steps;
}

function startServer() {
  const proc = spawn(MCP_CMD, MCP_ARGS, {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, NODE_NO_WARNINGS: '1' }
  });
  let buffer = '';
  let nextId = 1;
  const pending = new Map();

  proc.stdout.on('data', (data) => {
    buffer += data.toString();
    const lines = buffer.split('\n');
    buffer = lines.pop();
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const msg = JSON.parse(line);
        if (msg.id && pending.has(msg.id)) {
          const { resolve, reject } = pending.get(msg.id);
          pending.delete(msg.id);
          if (msg.error) reject(new Error(msg.error.message || JSON.stringify(msg.error)));
          else resolve(msg.result);
        }
      } catch (e) { /* skip */ }
    }
  });

  proc.stderr.on('data', (d) => process.stderr.write(d));

  function call(method, params) {
    return new Promise((resolve, reject) => {
      const id = nextId++;
      pending.set(id, { resolve, reject });
      proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    });
  }

  return { proc, call };
}

function buildCall(step) {
  const f = step.flags;
  const file = f.file || f['file-path'];
  const out = f.out || f['save-to-local-path'];
  const mode = f.mode || 'clean';

  switch (step.op) {
    case 'read': return {
      name: 'read_file',
      args: {
        file_path: file,
        format: f.format || 'json',
        ...(f.offset ? { offset: parseInt(f.offset) } : {}),
        ...(f.limit ? { limit: parseInt(f.limit) } : {}),
      }
    };

    case 'grep': return {
      name: 'grep',
      args: { file_path: file, pattern: f.pattern || f.query }
    };

    case 'replace': {
      if (!f.para || !f.old || f.new === undefined) throw new Error('replace needs --para, --old, --new');
      return {
        name: 'replace_text',
        args: {
          file_path: file,
          target_paragraph_id: f.para,
          old_string: f.old,
          new_string: f.new,
          instruction: f.desc || 'Replace text'
        }
      };
    }

    case 'comment': {
      if (!f.author || !f.text) throw new Error('comment needs --author, --text');
      const args = { file_path: file, author: f.author, text: f.text };
      if (f.para) args.target_paragraph_id = f.para;
      if (f['anchor-text']) args.anchor_text = f['anchor-text'];
      if (f['reply-to']) args.parent_comment_id = parseInt(f['reply-to']);
      if (f.initials) args.initials = f.initials;
      return { name: 'add_comment', args };
    }

    case 'get-comments': return {
      name: 'get_comments',
      args: { file_path: file }
    };

    case 'footnote': {
      if (!f.para || !f.text) throw new Error('footnote needs --para, --text');
      return {
        name: 'add_footnote',
        args: { file_path: file, target_paragraph_id: f.para, text: f.text }
      };
    }

    case 'save': {
      if (!out) throw new Error('save needs --out');
      const args = {
        file_path: file,
        save_to_local_path: out,
        save_format: mode === 'both' ? 'both' : (mode === 'tracked' ? 'tracked' : 'clean'),
        allow_overwrite: f.force === true || f.overwrite === true,
      };
      if (mode === 'both' || f['tracked-out']) {
        args.tracked_save_to_local_path = f['tracked-out'] || out.replace(/\.docx$/i, '') + '_tracked.docx';
      }
      return { name: 'save', args };
    }

    case 'compare': {
      if (!f.original || !f.revised || !out) throw new Error('compare needs --original, --revised, --out');
      return {
        name: 'compare_documents',
        args: {
          original_file_path: f.original,
          revised_file_path: f.revised,
          save_to_local_path: out,
          author: f.author || 'Comparison'
        }
      };
    }

    default: throw new Error(`Unknown operation: ${step.op}`);
  }
}

async function main() {
  const steps = parsePipeline();
  const { proc, call } = startServer();

  try {
    await call('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'docx-helper', version: '1.0' }
    });
    call('notifications/initialized', {}).catch(() => {});

    for (const step of steps) {
      const { name, args } = buildCall(step);
      const result = await call('tools/call', { name, arguments: args });

      const label = `${step.op}: `;
      if (result.content?.length > 0) {
        for (const part of result.content) {
          if (part.type === 'text') {
            try {
              const obj = JSON.parse(part.text);
              console.log(label + JSON.stringify(obj, null, 2));
              if (obj.success === false) process.exitCode = 1;
            } catch {
              console.log(label + part.text);
            }
          }
        }
      }
      if (result.isError) process.exitCode = 1;
    }
  } catch (e) {
    console.error('Error:', e.message);
    process.exit(1);
  } finally {
    // Clean up server-side temp files before killing the process.
    // Without this, close_file never runs and /tmp/safe-docx-* dirs leak.
    try {
      await call('tools/call', {
        name: 'close_file',
        arguments: { clear_all: true, confirm: true },
      });
    } catch {
      // Server may already be dead; ignore cleanup failures.
    }
    proc.kill();
    setTimeout(() => process.exit(process.exitCode || 0), 200);
  }
}

main();
