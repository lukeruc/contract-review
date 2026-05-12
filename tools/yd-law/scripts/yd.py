#!/usr/bin/env python3
"""YD 法律数据检索 CLI — 统一入口脚本。

用法:
  python yd.py case search --qw "违约金" --ay "买卖合同纠纷" -n 5
  python yd.py case detail --ah "（2023）京0101民初123号" --type ptal
  python yd.py case semantic --query "入户盗窃后自首" -n 5
  python yd.py statute search --keyword "行政处罚" -n 10
  python yd.py statute detail --fgmc "中华人民共和国刑法" --ftnum "第一百条"
  python yd.py law search --keyword "行政处罚" -n 10
  python yd.py law detail --fgmc "中华人民共和国刑法"
  python yd.py law semantic --query "入户盗窃" -n 10

API Key 从环境变量 YD_KEY 读取，也可通过 --api-key 传入。
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

BASE_URL = "https://open.chineselaw.com"


def get_api_key():
    key = os.environ.get("YD_KEY")
    if not key:
        print("错误: 未设置 YD_KEY 环境变量。请先执行: export YD_KEY=\"sk_...\"", file=sys.stderr)
        sys.exit(1)
    return key


def api_post(path, body, api_key):
    url = BASE_URL + path
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-API-Key", api_key)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "message": e.reason}


def api_get(path, params, api_key):
    from urllib.parse import urlencode
    url = BASE_URL + path + "?" + urlencode(params)
    req = urllib.request.Request(url, method="GET")
    req.add_header("X-API-Key", api_key)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "message": e.reason}


def add_case_search_args(sub):
    sub.add_argument("--ah", help="案号")
    sub.add_argument("--title", help="标题（精确短语匹配）")
    sub.add_argument("--ssqy", help="涉诉企业名称")
    sub.add_argument("--ay", action="append", default=[], help="案由（可重复）")
    sub.add_argument("--jbdw", action="append", default=[], help="经办法院（可重复）")
    sub.add_argument("--xzqh-p", action="append", default=[], dest="xzqh_p",
                     help="省级行政区（可重复）")
    sub.add_argument("--wszl", action="append", default=[], help="文书种类（可重复）")
    sub.add_argument("--ajlb", help="案件类别")
    sub.add_argument("--ja-start", help="结案日期起 yyyy-MM-dd")
    sub.add_argument("--ja-end", help="结案日期止 yyyy-MM-dd")
    sub.add_argument("--qw", help="全文关键词（空格分隔）")
    sub.add_argument("--fxgc", help="分析过程关键词")
    sub.add_argument("--search-mode", default="and", choices=["and", "or"],
                     help="关键词拼接模式，默认 and")
    sub.add_argument("--yyft", action="append", default=[],
                     help="援引法条，形如'中华人民共和国刑法第二条'（可重复）")
    sub.add_argument("--ft-search-mode", choices=["and", "or"],
                     help="法条拼接模式，默认 and")
    sub.add_argument("-n", "--top-k", type=int, default=10, dest="top_k",
                     help="返回条数，默认 10，最大 50")


def build_case_search_body(args):
    body = {}
    for key in ["ah", "title", "ssqy", "ajlb", "ja_start", "ja_end", "qw",
                "fxgc", "search_mode", "ft_search_mode"]:
        if getattr(args, key, None):
            body[key] = getattr(args, key)
    for list_key in ["ay", "jbdw", "xzqh_p", "wszl", "yyft"]:
        val = getattr(args, list_key, [])
        if val:
            body[list_key] = val
    body["top_k"] = args.top_k
    return body


def add_case_detail_args(sub):
    sub.add_argument("--id", help="案例 ID")
    sub.add_argument("--ah", help="案号")
    sub.add_argument("--type", required=True, choices=["ptal", "qwal"],
                     help="ptal=普通案例, qwal=权威案例")


def add_case_semantic_args(sub):
    sub.add_argument("--query", required=True, help="查询文本")
    sub.add_argument("--no-rewrite", action="store_true", help="禁用查询改写")
    sub.add_argument("--wenshu-type", help="案件类别")
    sub.add_argument("--wszl", action="append", default=[], help="文书种类编码（可重复）")
    sub.add_argument("--ja-start", help="结案日期起 yyyy-MM-dd")
    sub.add_argument("--ja-end", help="结案日期止 yyyy-MM-dd")
    sub.add_argument("--dianxing", action="store_true", help="仅典型案例")
    sub.add_argument("--fayuan", action="append", default=[], help="法院名称（可重复）")
    sub.add_argument("--cj", help="法院层级")
    sub.add_argument("--xzqh-p", dest="xzqh_p", help="省级行政区")
    sub.add_argument("--xzqh-c", dest="xzqh_c", help="市级行政区")
    sub.add_argument("-n", "--return-num", type=int, default=45, dest="return_num",
                     help="返回数量，默认 45")


def build_case_semantic_body(args):
    body = {"query": args.query, "rewrite_flag": not args.no_rewrite,
            "return_num": args.return_num}
    wenshu_filter = {}
    if args.wenshu_type:
        wenshu_filter["wenshu_type"] = args.wenshu_type
    if args.wszl:
        wenshu_filter["wszl"] = args.wszl
    if args.ja_start:
        wenshu_filter["ja_start"] = args.ja_start
    if args.ja_end:
        wenshu_filter["ja_end"] = args.ja_end
    if args.dianxing:
        wenshu_filter["dianxing"] = True
    if args.fayuan:
        wenshu_filter["fayuan"] = args.fayuan
    if args.cj:
        wenshu_filter["cj"] = args.cj
    if args.xzqh_p:
        wenshu_filter["xzqh_p"] = args.xzqh_p
    if args.xzqh_c:
        wenshu_filter["xzqh_c"] = args.xzqh_c
    if wenshu_filter:
        body["wenshu_filter"] = wenshu_filter
    return body


def add_statute_search_args(sub):
    sub.add_argument("--keyword", required=True, help="法条内容关键词")
    sub.add_argument("--search-mode", default="AND", choices=["AND", "OR"],
                     help="关键词拼接模式，默认 AND")
    sub.add_argument("--fgmc", help="法规名称过滤")
    sub.add_argument("--xljb-1", dest="xljb_1", help="效力级别过滤")
    sub.add_argument("--sxx", help="时效性过滤")
    sub.add_argument("--fbrq-start", help="发布日期起 yyyy-MM-dd")
    sub.add_argument("--fbrq-end", help="发布日期止 yyyy-MM-dd")
    sub.add_argument("--ssrq-start", help="实施日期起 yyyy-MM-dd")
    sub.add_argument("--ssrq-end", help="实施日期止 yyyy-MM-dd")
    sub.add_argument("-n", "--top-k", type=int, default=10, dest="top_k",
                     help="返回条数，默认 10，最大 50")


def build_statute_search_body(args):
    body = {"keyword": args.keyword, "search_mode": args.search_mode,
            "top_k": args.top_k}
    for key in ["fgmc", "xljb_1", "sxx", "fbrq_start", "fbrq_end",
                "ssrq_start", "ssrq_end"]:
        if getattr(args, key, None):
            body[key] = getattr(args, key)
    return body


def add_statute_detail_args(sub):
    sub.add_argument("--id", help="法条 ID")
    sub.add_argument("--fgmc", help="法规名称")
    sub.add_argument("--ftnum", help="法条号/名称")
    sub.add_argument("--refer-date", help="参考日期 yyyy-MM-dd")


def build_statute_detail_body(args):
    body = {}
    if args.id:
        body["id"] = args.id
    if args.fgmc:
        body["fgmc"] = args.fgmc
    if args.ftnum:
        body["ftnum"] = args.ftnum
    if args.refer_date:
        body["refer_date"] = args.refer_date
    return body


def add_law_search_args(sub):
    sub.add_argument("--keyword", help="法规内容关键词（可不传，仅按条件过滤）")
    sub.add_argument("--search-mode", default="AND", choices=["AND", "OR"],
                     help="关键词拼接模式，默认 AND")
    sub.add_argument("--fgmc", help="法规名称过滤")
    sub.add_argument("--sxx", help="时效性过滤")
    sub.add_argument("--xljb-1", dest="xljb_1", help="效力级别过滤")
    sub.add_argument("--fbrq-start", help="发布日期起 yyyy-MM-dd")
    sub.add_argument("--fbrq-end", help="发布日期止 yyyy-MM-dd")
    sub.add_argument("--ssrq-start", help="实施日期起 yyyy-MM-dd")
    sub.add_argument("--ssrq-end", help="实施日期止 yyyy-MM-dd")
    sub.add_argument("-n", "--top-k", type=int, default=10, dest="top_k",
                     help="返回条数，默认 10，最大 50")


def build_law_search_body(args):
    body = {"search_mode": args.search_mode, "top_k": args.top_k}
    if args.keyword:
        body["keyword"] = args.keyword
    for key in ["fgmc", "sxx", "xljb_1", "fbrq_start", "fbrq_end",
                "ssrq_start", "ssrq_end"]:
        if getattr(args, key, None):
            body[key] = getattr(args, key)
    return body


def add_law_detail_args(sub):
    sub.add_argument("--id", help="法规 ID")
    sub.add_argument("--fgmc", help="法规名称")
    sub.add_argument("--refer-date", help="参考日期 yyyy-MM-dd")


def build_law_detail_body(args):
    body = {}
    if args.id:
        body["id"] = args.id
    if args.fgmc:
        body["fgmc"] = args.fgmc
    if args.refer_date:
        body["refer_date"] = args.refer_date
    return body


def add_law_semantic_args(sub):
    sub.add_argument("--query", required=True, help="查询文本")
    sub.add_argument("--no-rewrite", action="store_true", help="禁用查询改写")
    sub.add_argument("--sxx", action="append", default=[], help="时效性（可重复）")
    sub.add_argument("--effect1", action="append", default=[], help="一级效力级别（可重复）")
    sub.add_argument("--law-start", help="法条生效起始日期 yyyy-MM-dd")
    sub.add_argument("--law-end", help="法条生效结束日期 yyyy-MM-dd")
    sub.add_argument("-n", "--return-num", type=int, default=45, dest="return_num",
                     help="返回数量，默认 45")


def build_law_semantic_body(args):
    body = {"query": args.query, "rewrite_flag": not args.no_rewrite,
            "return_num": args.return_num}
    fatiao_filter = {}
    if args.sxx:
        fatiao_filter["sxx"] = args.sxx
    if args.effect1:
        fatiao_filter["effect1"] = args.effect1
    if args.law_start:
        fatiao_filter["law_start"] = args.law_start
    if args.law_end:
        fatiao_filter["law_end"] = args.law_end
    if fatiao_filter:
        body["fatiao_filter"] = fatiao_filter
    return body


def main():
    parser = argparse.ArgumentParser(
        description="YD 法律数据检索 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python yd.py case search --qw "违约金" --ay "买卖合同纠纷" -n 5
  python yd.py case detail --ah "（2023）京0101民初123号" --type ptal
  python yd.py case semantic --query "入户盗窃后自首" -n 5
  python yd.py statute search --keyword "行政处罚" -n 10
  python yd.py statute detail --fgmc "中华人民共和国刑法" --ftnum "第一百条"
  python yd.py law search --keyword "行政处罚" -n 10
  python yd.py law detail --fgmc "中华人民共和国刑法"
  python yd.py law semantic --query "入户盗窃"
        """)
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # ---- case ----
    case_parser = subparsers.add_parser("case", help="案例相关操作")
    case_sub = case_parser.add_subparsers(dest="action")
    case_search = case_sub.add_parser("search", help="关键词检索案例")
    add_case_search_args(case_search)
    case_detail = case_sub.add_parser("detail", help="案例详情")
    add_case_detail_args(case_detail)
    case_semantic = case_sub.add_parser("semantic", help="语义检索案例")
    add_case_semantic_args(case_semantic)

    # ---- statute ----
    statute_parser = subparsers.add_parser("statute", help="法条相关操作")
    statute_sub = statute_parser.add_subparsers(dest="action")
    statute_search = statute_sub.add_parser("search", help="关键词检索法条")
    add_statute_search_args(statute_search)
    statute_detail = statute_sub.add_parser("detail", help="法条详情")
    add_statute_detail_args(statute_detail)

    # ---- law ----
    law_parser = subparsers.add_parser("law", help="法规相关操作")
    law_sub = law_parser.add_subparsers(dest="action")
    law_search = law_sub.add_parser("search", help="关键词检索法规")
    add_law_search_args(law_search)
    law_detail = law_sub.add_parser("detail", help="法规详情")
    add_law_detail_args(law_detail)
    law_semantic = law_sub.add_parser("semantic", help="语义检索法律法规")
    add_law_semantic_args(law_semantic)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    api_key = get_api_key()

    # Route to API
    if args.command == "case":
        if args.action == "search":
            result = api_post("/open/rh_ptal_search",
                              build_case_search_body(args), api_key)
        elif args.action == "detail":
            params = {}
            if args.id:
                params["id"] = args.id
            if args.ah:
                params["ah"] = args.ah
            params["type"] = args.type
            result = api_get("/open/rh_case_details", params, api_key)
        elif args.action == "semantic":
            result = api_post("/open/case_vector_search",
                              build_case_semantic_body(args), api_key)
        else:
            case_parser.print_help()
            sys.exit(1)

    elif args.command == "statute":
        if args.action == "search":
            result = api_post("/open/rh_ft_search",
                              build_statute_search_body(args), api_key)
        elif args.action == "detail":
            result = api_post("/open/rh_ft_detail",
                              build_statute_detail_body(args), api_key)
        else:
            statute_parser.print_help()
            sys.exit(1)

    elif args.command == "law":
        if args.action == "search":
            result = api_post("/open/rh_fg_search",
                              build_law_search_body(args), api_key)
        elif args.action == "detail":
            result = api_post("/open/rh_fg_detail",
                              build_law_detail_body(args), api_key)
        elif args.action == "semantic":
            result = api_post("/open/law_vector_search",
                              build_law_semantic_body(args), api_key)
        else:
            law_parser.print_help()
            sys.exit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
