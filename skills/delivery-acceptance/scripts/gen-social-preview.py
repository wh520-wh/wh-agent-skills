# 生成 GitHub 社交预览图 (1280x640 PNG)
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
BG = (15, 17, 24)            # 深色背景
ACCENT = (155, 124, 255)     # 紫色强调（提亮 +30 提高对比度）
TEXT = (235, 238, 245)
SUB = (150, 158, 175)
LINK = (200, 208, 222)       # 链接（提亮，引导访问）
HOOK = (255, 200, 90)        # 钩子橙黄

# 安全内边距（避免社交平台缩略图切边）
PAD_X = 90
PAD_TOP = 90

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

f_title = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 78)
f_cn = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 44)
f_hook = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 40)
f_badge = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
f_tag = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)

# 左侧紫色竖条（视觉锚点）
d.rectangle([0, 0, 14, H], fill=ACCENT)

# 顶部小标签（带安全边距）
d.text((PAD_X, PAD_TOP), "Agent Skill · Claude Code / Codex / OpenClaw", font=f_tag, fill=SUB)

# 主标题
d.text((PAD_X, PAD_TOP + 60), "delivery-acceptance", font=f_title, fill=TEXT)
# 中文副标（提亮的紫色）
d.text((PAD_X, PAD_TOP + 165), "YANSHOU 验收", font=f_cn, fill=ACCENT)

# 钩子
d.text((PAD_X, PAD_TOP + 250), "「测试全绿」不是验收，是自述。", font=f_hook, fill=HOOK)
d.text((PAD_X, PAD_TOP + 305), "假设交付是错的，用探针证明它真假，再闭环修到可合并。", font=f_badge, fill=TEXT)

# 亮点徽章行（统一风格：深色填充 + 浅色边框 + 紫色强调点）
badges = ["三维度验收", "必跑探针", "全闭环修复", "零 Key", "无人值守"]
x = PAD_X
y = PAD_TOP + 400
BADGE_BG = (28, 32, 44)
BADGE_BORDER = (70, 80, 105)
DOT = ACCENT  # 用紫色小圆点做强调，呼应左侧竖条
for label in badges:
    tw = d.textlength(label, font=f_badge)
    bw = tw + 60  # 留圆点位置
    d.rounded_rectangle([x, y, x + bw, y + 52], radius=26,
                        fill=BADGE_BG, outline=BADGE_BORDER, width=2)
    # 紫色小圆点
    d.ellipse([x + 18, y + 22, x + 28, y + 32], fill=DOT)
    d.text((x + 36, y + 10), label, font=f_badge, fill=TEXT)
    x += bw + 16

# 右侧装饰：极简的"探针/校验勾"线条图形，平衡左右视觉
def draw_decoration(d, cx, cy):
    """画一个由检查标记 + 圆环组成的极简徽记"""
    ring_color = (60, 70, 95)
    check_color = ACCENT
    # 外圆环
    d.ellipse([cx-130, cy-130, cx+130, cy+130], outline=ring_color, width=4)
    d.ellipse([cx-95, cy-95, cx+95, cy+95], outline=ring_color, width=3)
    # 内圈勾选标记 ✓
    d.line([(cx-50, cy+5), (cx-15, cy+40), (cx+55, cy-40)], fill=check_color, width=10)

draw_decoration(d, W - 200, H // 2 - 30)

# 底部署名（提亮的链接色）
d.text((PAD_X, H - 60), "github.com/", font=f_tag, fill=SUB)
gh_w = d.textlength("github.com/", font=f_tag)
d.text((PAD_X + gh_w, H - 60), "wh520-wh/delivery-acceptance-yanshou", font=f_tag, fill=LINK)

img.save("social-preview.png")
print("saved social-preview.png", img.size)

