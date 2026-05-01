"""
xhs-survey v2.0 — 模拟真人浏览采集小红书数据
用法: python xhs_survey_collector.py "关键词1" "关键词2" ...
"""
import sys
import io
import os
import json
import time
import random
import re
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright

# ============================================================
# 配置
# ============================================================
COOKIE_FILE = 'D:/claude/xhs_cookie.txt'
OUTPUT_DIR = 'D:/claude/xhs_research'   # 输出目录
MAX_NOTES_PER_KEYWORD = 20      # 每个关键词最多采集笔记数
MAX_SCROLL_ROUNDS = 12          # 每页最多滚动轮数
SCROLL_DELAY_MIN = 1.5          # 滚动后最小等待（秒）
SCROLL_DELAY_MAX = 3.5          # 滚动后最大等待（秒）
NOTE_READ_MIN = 2.0             # 阅读笔记最小等待（秒）
NOTE_READ_MAX = 4.5             # 阅读笔记最大等待（秒）
BETWEEN_NOTES_MIN = 1.0         # 笔记之间最小间隔（秒）
BETWEEN_NOTES_MAX = 2.5         # 笔记之间最大间隔（秒）


# ============================================================
# Cookie 加载
# ============================================================
def load_cookies(cookie_file=COOKIE_FILE):
    if not os.path.exists(cookie_file):
        print(f'[ERROR] Cookie file not found: {cookie_file}')
        return None
    with open(cookie_file, 'r', encoding='utf-8') as f:
        cookie_str = f.read().strip()
    cookies = []
    for pair in cookie_str.split(';'):
        pair = pair.strip()
        if '=' in pair:
            name, value = pair.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.xiaohongshu.com',
                'path': '/',
            })
    return cookies


# ============================================================
# 数值解析
# ============================================================
def parse_count(val):
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        val = val.strip().replace(',', '')
        if '万' in val:
            return int(float(val.replace('万', '')) * 10000)
        if '亿' in val:
            return int(float(val.replace('亿', '')) * 100000000)
        try:
            return int(val)
        except ValueError:
            return 0
    return 0


# ============================================================
# 人类行为模拟
# ============================================================
def human_scroll(page, distance=None):
    """模拟人类滚动：先快后慢，有惯性"""
    if distance is None:
        distance = random.randint(300, 900)
    steps = random.randint(3, 6)
    for i in range(steps):
        step_dist = distance // steps + random.randint(-20, 20)
        page.evaluate(f'window.scrollBy(0, {step_dist})')
        time.sleep(random.uniform(0.05, 0.15))
    time.sleep(random.uniform(SCROLL_DELAY_MIN, SCROLL_DELAY_MAX))


def human_scroll_up(page, distance=None):
    """模拟人类向上滚动"""
    if distance is None:
        distance = random.randint(200, 500)
    steps = random.randint(2, 4)
    for i in range(steps):
        step_dist = -(distance // steps)
        page.evaluate(f'window.scrollBy(0, {step_dist})')
        time.sleep(random.uniform(0.05, 0.12))
    time.sleep(random.uniform(1.0, 2.0))


def human_mouse_move(page, x=None, y=None):
    """模拟人类鼠标移动"""
    if x is None:
        x = random.randint(200, 1400)
    if y is None:
        y = random.randint(200, 800)
    page.mouse.move(x, y, steps=random.randint(5, 15))
    time.sleep(random.uniform(0.2, 0.5))


def human_wait(min_s, max_s):
    """随机等待"""
    time.sleep(random.uniform(min_s, max_s))


# ============================================================
# 搜索结果页：提取当前可见的笔记链接
# ============================================================
def extract_visible_notes(page):
    """从搜索结果页提取当前可见区域的笔记信息"""
    return page.evaluate("""() => {
        const results = [];
        const links = document.querySelectorAll('a[href*="/explore/"]');
        for (const link of links) {
            const href = link.href;
            const match = href.match(/explore\\/([a-f0-9]+)/);
            if (!match) continue;
            const nid = match[1];

            // 获取笔记卡片容器
            const container = link.closest('section') || link.closest('div[class*="note"]') || link.parentElement;
            if (!container) continue;

            // 提取标题
            const titleEl = container.querySelector('[class*="title"] span, [class*="title"]');
            const title = titleEl?.textContent?.trim() || '';

            // 提取作者
            const authorEl = container.querySelector('[class*="name"], [class*="nickname"]');
            const author = authorEl?.textContent?.trim() || '';

            // 提取点赞数
            const likeEl = container.querySelector('[class*="like"] span, [class*="count"]');
            const likes = likeEl?.textContent?.trim() || '0';

            // 检查是否已处理
            results.push({
                note_id: nid,
                title: title,
                author: author,
                likes_text: likes,
                url: href,
            });
        }
        return results;
    }""")


# ============================================================
# 笔记详情页：读取完整内容
# ============================================================
def read_note_detail(page, note_url):
    """点击进入笔记详情页，读取完整内容"""
    detail = {
        'title': '',
        'desc': '',
        'author': '',
        'likes': 0,
        'collected': 0,
        'comments': 0,
        'shared': 0,
        'tags': [],
        'type': 'image',
    }

    try:
        page.goto(note_url, wait_until='domcontentloaded', timeout=15000)
        human_wait(NOTE_READ_MIN, NOTE_READ_MAX)

        # 尝试从 SSR 数据提取
        ssr_data = page.evaluate("""() => {
            try {
                const scripts = document.querySelectorAll('script');
                for (const s of scripts) {
                    const text = s.textContent;
                    if (text.includes('__INITIAL_STATE__')) {
                        const match = text.match(/window\\.__INITIAL_STATE__\\s*=\\s*({.*?})\\s*;?\\s*<\\/script>/s);
                        if (match) {
                            const parsed = JSON.parse(match[1].replace(/undefined/g, 'null'));
                            const noteMap = parsed.note?.noteDetailMap;
                            if (noteMap) {
                                for (const [k, v] of Object.entries(noteMap)) {
                                    if (k !== 'null' && v) {
                                        const note = v.note || v;
                                        return {
                                            title: note.title || '',
                                            desc: note.desc || '',
                                            author: note.user?.nickname || '',
                                            likes: note.interact_info?.liked_count || 0,
                                            collected: note.interact_info?.collected_count || 0,
                                            comments: note.interact_info?.comment_count || 0,
                                            shared: note.interact_info?.shared_count || 0,
                                            tags: (note.tag_list || []).map(t => t.name).filter(Boolean),
                                            type: note.type === 'video' ? 'video' : 'image',
                                            from_ssr: true,
                                        };
                                    }
                                }
                            }
                        }
                    }
                }
            } catch(e) {}
            return null;
        }""")

        if ssr_data and ssr_data.get('title'):
            detail.update(ssr_data)
            return detail

        # DOM 提取
        dom_data = page.evaluate("""() => {
            const data = {};

            const titleEl = document.querySelector('#detail-title, [class*="title"][class*="note"]');
            data.title = titleEl?.textContent?.trim() || '';

            const descEl = document.querySelector('#detail-desc, .note-text, [class*="desc"][class*="note"]');
            data.desc = descEl?.textContent?.trim()?.substring(0, 500) || '';

            const authorEl = document.querySelector('.author-wrapper .username, [class*="author"] [class*="name"]');
            data.author = authorEl?.textContent?.trim() || '';

            const likeEl = document.querySelector('[class*="like-wrapper"] .count, [class*="like"] [class*="count"]');
            data.likes = likeEl?.textContent?.trim() || '0';

            const collectEl = document.querySelector('[class*="collect-wrapper"] .count, [class*="collect"] [class*="count"]');
            data.collected = collectEl?.textContent?.trim() || '0';

            const commentEl = document.querySelector('[class*="chat-wrapper"] .count, [class*="comment"] [class*="count"]');
            data.comments = commentEl?.textContent?.trim() || '0';

            const tagEls = document.querySelectorAll('.tag a, [class*="hash-tag"], a[href*="/search_result?keyword="]');
            data.tags = Array.from(tagEls).map(t => t.textContent.trim().replace(/^#/, '')).filter(t => t && t.length < 20);

            if (document.querySelector('video, [class*="video-player"]')) {
                data.type = 'video';
            }

            return data;
        }""")

        if dom_data:
            detail['title'] = dom_data.get('title', '')
            detail['desc'] = dom_data.get('desc', '')
            detail['author'] = dom_data.get('author', '')
            detail['likes'] = parse_count(dom_data.get('likes', 0))
            detail['collected'] = parse_count(dom_data.get('collected', 0))
            detail['comments'] = parse_count(dom_data.get('comments', 0))
            detail['tags'] = dom_data.get('tags', [])
            detail['type'] = dom_data.get('type', 'image')

    except Exception as e:
        print(f'    [WARN] Failed to read note detail: {e}')

    return detail


# ============================================================
# 主采集流程：模拟真人浏览
# ============================================================
def browse_and_collect(page, keyword, sort_type=1, sort_name='hot'):
    """模拟真人浏览搜索结果并采集数据"""
    notes = []
    visited_ids = set()
    api_captures = []

    # API 拦截
    def on_response(response):
        if 'search/notes' in response.url:
            try:
                data = response.json()
                for item in data.get('data', {}).get('items', []):
                    note = item.get('note_card', {})
                    nid = item.get('id', '')
                    if nid:
                        api_captures.append({
                            'note_id': nid,
                            'title': note.get('display_title', note.get('title', '')),
                            'author': note.get('user', {}).get('nickname', ''),
                            'likes': parse_count(note.get('interact_info', {}).get('liked_count', 0)),
                            'collected': parse_count(note.get('interact_info', {}).get('collected_count', 0)),
                            'comments': parse_count(note.get('interact_info', {}).get('comment_count', 0)),
                            'shared': parse_count(note.get('interact_info', {}).get('shared_count', 0)),
                            'type': 'video' if 'video' in str(note.get('type', '')).lower() else 'image',
                            'tags': [t.get('name', '') for t in note.get('tag_list', []) if t.get('name')],
                        })
            except Exception:
                pass

    page.on('response', on_response)

    # 打开搜索页面
    url = f'https://www.xiaohongshu.com/search_result?keyword={keyword}&sort={sort_type}&source=web_search_result_notes'
    print(f'  [BROWSE] Opening: {keyword} (sort={sort_name})')

    try:
        page.goto(url, wait_until='domcontentloaded', timeout=20000)
    except Exception:
        try:
            page.goto(url, wait_until='commit', timeout=20000)
        except Exception as e:
            print(f'  [ERROR] Cannot open page: {e}')
            page.remove_listener('response', on_response)
            return notes

    human_wait(5, 8)

    # 模拟人类：先看看页面，移动鼠标
    human_mouse_move(page)
    human_wait(1, 2)

    # 滚动浏览 + 点击进入笔记
    no_new_count = 0
    for round_num in range(MAX_SCROLL_ROUNDS):
        if len(notes) >= MAX_NOTES_PER_KEYWORD:
            print(f'  [INFO] Reached max notes ({MAX_NOTES_PER_KEYWORD})')
            break

        # 提取当前可见的笔记
        visible = extract_visible_notes(page)
        new_visible = [n for n in visible if n['note_id'] not in visited_ids]

        if not new_visible:
            no_new_count += 1
            if no_new_count >= 3:
                print(f'  [INFO] No new notes found after {no_new_count} scrolls, stopping')
                break
            # 继续滚动
            human_scroll(page)
            continue

        no_new_count = 0

        # 逐个点击进入笔记详情
        for note_info in new_visible[:5]:  # 每轮最多点击 5 篇
            nid = note_info['note_id']
            if nid in visited_ids:
                continue
            visited_ids.add(nid)

            print(f'    [{len(notes)+1}] Clicking: {nid} ({note_info.get("author", "unknown")})', end='')

            # 进入笔记详情页
            try:
                note_url = f'https://www.xiaohongshu.com/explore/{nid}'
                # 方式1: 尝试 JS 模拟点击
                js_clicked = page.evaluate(f"""() => {{
                    const links = document.querySelectorAll('a[href*="{nid}"]');
                    for (const l of links) {{
                        const rect = l.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && rect.top >= 0) {{
                            l.dispatchEvent(new MouseEvent('click', {{bubbles: true}}));
                            return true;
                        }}
                    }}
                    return false;
                }}""")

                if not js_clicked:
                    # 方式2: 直接导航
                    page.goto(note_url, wait_until='domcontentloaded', timeout=15000)

                human_wait(NOTE_READ_MIN, NOTE_READ_MAX)

                # 读取笔记详情
                detail = read_note_detail(page, note_url)

                # 合并数据
                note = {
                    'note_id': nid,
                    'title': detail.get('title') or note_info.get('title', ''),
                    'desc': detail.get('desc', '')[:300],
                    'author': detail.get('author') or note_info.get('author', ''),
                    'type': detail.get('type', 'image'),
                    'likes': detail.get('likes') or parse_count(note_info.get('likes_text', '0')),
                    'collected': detail.get('collected', 0),
                    'comments': detail.get('comments', 0),
                    'shared': detail.get('shared', 0),
                    'tags': detail.get('tags', []),
                    'url': note_url,
                    'keyword': keyword,
                }
                notes.append(note)

                title_preview = note['title'][:30] or '(no title)'
                print(f' -> {title_preview} | {note["likes"]}L {note["collected"]}C {note["comments"]}CM')

                # 返回搜索结果页
                try:
                    page.go_back()
                    human_wait(1.5, 3.0)
                except Exception:
                    pass

                # 确认回到搜索页
                if 'search_result' not in page.url:
                    try:
                        page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        human_wait(3, 5)
                    except Exception:
                        pass

            except Exception as e:
                print(f' -> error: {str(e)[:80]}')
                # 恢复到搜索页
                try:
                    page.go_back()
                    human_wait(1, 2)
                except Exception:
                    pass
                if 'search_result' not in page.url:
                    try:
                        page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        human_wait(2, 4)
                    except Exception:
                        pass

            human_wait(BETWEEN_NOTES_MIN, BETWEEN_NOTES_MAX)

        # 向下滚动查看更多
        human_scroll(page)

        # 随机向上滚一点（模拟人类回看行为）
        if random.random() < 0.2:
            human_scroll_up(page, random.randint(100, 300))
            human_wait(0.5, 1.0)

    page.remove_listener('response', on_response)

    # 合并 API 拦截到的数据（补充未点击的笔记）
    api_by_id = {n['note_id']: n for n in api_captures if n.get('note_id')}
    for nid, api_note in api_by_id.items():
        if nid not in visited_ids:
            notes.append({
                'note_id': nid,
                'title': api_note.get('title', ''),
                'desc': '',
                'author': api_note.get('author', ''),
                'type': api_note.get('type', 'image'),
                'likes': api_note.get('likes', 0),
                'collected': api_note.get('collected', 0),
                'comments': api_note.get('comments', 0),
                'shared': api_note.get('shared', 0),
                'tags': api_note.get('tags', []),
                'url': f'https://www.xiaohongshu.com/explore/{nid}',
                'keyword': keyword,
                'from_api': True,
            })

    return notes


# ============================================================
# 报告生成
# ============================================================
def generate_report(notes, keywords):
    if not notes:
        return 'No data collected.'

    # 去重
    seen = set()
    unique = []
    for n in notes:
        nid = n.get('note_id')
        if nid and nid not in seen:
            seen.add(nid)
            unique.append(n)
    notes = unique

    total = len(notes)
    total_likes = sum(n.get('likes', 0) for n in notes)
    total_collected = sum(n.get('collected', 0) for n in notes)
    total_comments = sum(n.get('comments', 0) for n in notes)
    total_shared = sum(n.get('shared', 0) for n in notes)

    for n in notes:
        n['engagement'] = n.get('likes', 0) + n.get('collected', 0) + n.get('comments', 0) + n.get('shared', 0)

    hot = sorted(notes, key=lambda x: x['engagement'], reverse=True)

    video_count = sum(1 for n in notes if n.get('type') == 'video')
    image_count = total - video_count

    # 作者统计
    author_freq = {}
    for n in notes:
        a = n.get('author', '')
        if a:
            author_freq[a] = author_freq.get(a, 0) + 1
    top_authors = sorted(author_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    # 标签统计
    tag_freq = {}
    for n in notes:
        for tag in n.get('tags', []):
            tag_freq[tag] = tag_freq.get(tag, 0) + 1
    top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:10]

    avg_likes = total_likes / total if total else 0
    avg_collected = total_collected / total if total else 0
    collect_rate = (total_collected / total_likes * 100) if total_likes else 0

    r = []
    r.append('=' * 60)
    r.append(f'  {" / ".join(keywords)} · 小红书影响力分析报告')
    r.append(f'  生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    r.append('=' * 60)

    r.append('\n  一、数据概览')
    r.append('-' * 40)
    r.append(f'  采集笔记总数: {total} 篇')
    r.append(f'  内容类型: 图文 {image_count} 篇 | 视频 {video_count} 篇')
    r.append(f'  总互动量: {total_likes + total_collected + total_comments + total_shared:,}')
    r.append(f'    总点赞:   {total_likes:,} (均值 {avg_likes:.0f})')
    r.append(f'    总收藏:   {total_collected:,} (均值 {avg_collected:.0f})')
    r.append(f'    总评论:   {total_comments:,}')
    r.append(f'    总转发:   {total_shared:,}')
    if total_likes > 0:
        r.append(f'  收藏率: {collect_rate:.1f}%')

    r.append('\n  二、最热笔记 TOP 10')
    r.append('-' * 40)
    for i, n in enumerate(hot[:10], 1):
        title = n.get('title', '(无标题)')[:50]
        r.append(f'\n  #{i} {title}')
        r.append(f'     作者: {n.get("author", "")} | 类型: {"视频" if n.get("type") == "video" else "图文"}')
        r.append(f'     点赞: {n.get("likes", 0):,}  收藏: {n.get("collected", 0):,}  评论: {n.get("comments", 0):,}')
        r.append(f'     总互动: {n["engagement"]:,}')
        if n.get('tags'):
            r.append(f'     标签: {", ".join(n["tags"][:5])}')
        if n.get('desc'):
            r.append(f'     摘要: {n["desc"][:80]}')
        r.append(f'     链接: {n.get("url", "")}')

    r.append('\n  三、最新笔记 TOP 10')
    r.append('-' * 40)
    for i, n in enumerate([n for n in notes if not n.get('from_api')][:10], 1):
        title = n.get('title', '(无标题)')[:50]
        r.append(f'\n  #{i} {title}')
        r.append(f'     作者: {n.get("author", "")} | 点赞: {n.get("likes", 0):,}')
        if n.get('desc'):
            r.append(f'     摘要: {n["desc"][:80]}')
        r.append(f'     链接: {n.get("url", "")}')

    if top_authors:
        r.append('\n  四、活跃作者 TOP 10')
        r.append('-' * 40)
        for author, count in top_authors:
            r.append(f'  {author}  {count} 篇')

    if top_tags:
        r.append('\n  五、热门标签')
        r.append('-' * 40)
        for tag, count in top_tags:
            r.append(f'  #{tag}  出现 {count} 次')

    # 影响力评分
    avg_eng = sum(n['engagement'] for n in notes) / total if total else 0
    volume_score = min(10, total / 10)
    quality_score = min(10, avg_eng / 300)
    diversity_score = min(10, (video_count / max(total, 1)) * 10 + (image_count / max(total, 1)) * 6)
    overall = quality_score * 0.5 + volume_score * 0.3 + diversity_score * 0.2

    r.append('\n  六、影响力评估')
    r.append('-' * 40)
    r.append(f'  内容体量分: {volume_score:.1f}/10')
    r.append(f'  互动质量分: {quality_score:.1f}/10')
    r.append(f'  内容多样分: {diversity_score:.1f}/10')
    r.append(f'  综合影响力: {overall:.1f}/10')

    if overall >= 7:
        level = '高影响力'
    elif overall >= 4:
        level = '中等影响力'
    else:
        level = '影响力有限'
    r.append(f'  评定等级: {level}')

    r.append('\n' + '=' * 60)
    return '\n'.join(r)


# ============================================================
# 主程序
# ============================================================
def main():
    if len(sys.argv) < 2:
        print('用法: python xhs_survey_collector.py "关键词1" "关键词2" ...')
        sys.exit(1)

    keywords = sys.argv[1:]
    print(f'[INFO] Keywords: {keywords}')

    cookies = load_cookies()
    if not cookies:
        print('[ERROR] Cookie not found.')
        sys.exit(1)
    print(f'[INFO] Loaded {len(cookies)} cookies')

    all_notes = []

    with sync_playwright() as p:
        print('[INFO] Launching Edge browser (visible mode)...')
        browser = p.chromium.launch(
            channel='msedge',
            headless=False,  # 可见模式，模拟真人
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check',
            ]
        )
        ctx = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        # 注入反检测脚本
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
        """)

        for kw in keywords:
            print(f'\n[KEYWORD] {kw}')

            # 最热排序
            notes = browse_and_collect(page, kw, sort_type=1, sort_name='hot')
            all_notes.extend(notes)
            print(f'  Collected {len(notes)} notes (hot)')

            # 随机等待后切换排序
            human_wait(3, 6)

            # 最新排序
            notes = browse_and_collect(page, kw, sort_type=2, sort_name='latest')
            all_notes.extend(notes)
            print(f'  Collected {len(notes)} notes (latest)')

            human_wait(2, 4)

        print(f'\n[INFO] Closing browser...')
        browser.close()

    # 去重
    seen = set()
    unique = []
    for n in all_notes:
        nid = n.get('note_id')
        if nid and nid not in seen:
            seen.add(nid)
            unique.append(n)
    all_notes = unique

    print(f'[INFO] Total unique notes: {len(all_notes)}')

    if not all_notes:
        print('[WARN] No data collected.')
        sys.exit(1)

    # 过滤蔚来地平线产品（与地平线公司无关）
    nio_keywords = ['蔚来', 'ES6', 'ES8', 'ET7', 'ET5', 'EC7', 'EC6', 'NIO', 'nio', '蔚来地平线']
    filtered = []
    for n in all_notes:
        title = (n.get('title', '') + n.get('desc', '')).lower()
        is_nio = any(kw.lower() in title for kw in nio_keywords)
        if not is_nio:
            filtered.append(n)
        else:
            print(f'  [FILTER] Excluded NIO note: {n.get("title", "")[:40]}')
    all_notes = filtered

    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 保存数据
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    data_file = os.path.join(OUTPUT_DIR, f'xhs_data_{timestamp}.json')
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(all_notes, f, ensure_ascii=False, indent=2)
    print(f'[INFO] Data saved: {data_file}')

    # 生成报告
    report = generate_report(all_notes, keywords)
    print(report)

    report_file = os.path.join(OUTPUT_DIR, f'xhs_report_{timestamp}.txt')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f'[INFO] Report saved: {report_file}')


if __name__ == '__main__':
    main()
