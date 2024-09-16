import pygame
import random
import time

# 初始化 Pygame
pygame.init()

# 设置窗口大小和标题
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("动了个物小游戏")

# 加载字体
font_path = "assets/SimHei.ttf"  # 请确保你的 assets 文件夹中有 SimHei.ttf 文件
font_large = pygame.font.Font(font_path, 55)
font_medium = pygame.font.Font(font_path, 45)
font_small = pygame.font.Font(font_path, 35)

# 加载图标和背景图，并调整大小
icon_size = (80, 80)  # 图标的固定大小
icons = [pygame.transform.scale(pygame.image.load(f'assets/cute_animal{i}.png'), icon_size) for i in range(1, 7)]
game_bg = pygame.image.load('assets/background.png')
garbage_bin_bg = pygame.image.load('assets/garbage_bin_bg.png')
menu_bg = pygame.image.load('assets/menu_bg.png')
finished_bg = pygame.image.load('assets/finished.png')  # 结算页面背景

# 缩放背景图和垃圾槽图，使其高度对齐
game_bg = pygame.transform.scale(game_bg, (SCREEN_WIDTH // 2, SCREEN_HEIGHT))
garbage_bin_bg = pygame.transform.scale(garbage_bin_bg, (SCREEN_WIDTH // 2, SCREEN_HEIGHT))

# 加载音乐和音效
pygame.mixer.music.load('assets/background_music.mp3')
click_sound = pygame.mixer.Sound('assets/click_sound.mp3')
match_sound = pygame.mixer.Sound('assets/success_sound.mp3')
success_sound = pygame.mixer.Sound('assets/success_sound.mp3')
failure_sound = pygame.mixer.Sound('assets/failure_sound.mp3')

# 常量
MENU, GAME, RESULT, HELP = 0, 1, 2, 3  # 游戏状态，新增 HELP 状态
EASY, MEDIUM, HARD = 0, 1, 2  # 难度
TIME_LIMIT = {EASY: 90, MEDIUM: 60, HARD: 45}  # 调整难度的时间限制
ICON_PAIRS = {EASY: 6, MEDIUM: 8, HARD: 12}

# 初始化游戏变量
game_state = MENU
difficulty = EASY
score = 0
time_left = TIME_LIMIT[difficulty]
selected_icons = []
matched_icons = []
icon_positions = []  # 存储图标的固定位置
hint_used = 0
undo_used = False
clicks = []
start_time = 0
game_over = False
game_result = ""
hint_index = None
undo_last_match = []

def shuffle_icons():
    """打乱图标并创建匹配对"""
    icons_pairs = icons * (ICON_PAIRS[difficulty] // len(icons))
    random.shuffle(icons_pairs)
    return icons_pairs[:ICON_PAIRS[difficulty]] * 2

def generate_icon_positions():
    """生成图标的固定位置，保证整齐排列"""
    positions = []
    rows = 4  # 固定4行
    cols = (ICON_PAIRS[difficulty] * 2) // rows  # 根据总图标数量确定列数
    for row in range(rows):
        for col in range(cols):
            x = col * (icon_size[0] + 20) + 50
            y = row * (icon_size[1] + 20) + 50
            positions.append((x, y))
    return positions

def handle_click(mouse_pos):
    global clicks, matched_icons, score, undo_last_match

    # 遍历所有图标，检查鼠标是否点击了某个图标
    for i, (x, y) in enumerate(icon_positions):
        if i not in matched_icons:  # 未匹配的图标才可以点击
            icon_rect = pygame.Rect(x, y, icon_size[0], icon_size[1])
            if icon_rect.collidepoint(mouse_pos):
                if i in clicks:
                    # 如果图标已经被选中，点击时取消选中
                    clicks.remove(i)
                else:
                    clicks.append(i)
                    # 检查是否选择了两个图标
                    if len(clicks) == 2:
                        check_match()

def check_match():
    global clicks, matched_icons, score, undo_last_match

    # 如果点击了两个图标，检查它们是否匹配
    if selected_icons[clicks[0]] == selected_icons[clicks[1]]:
        # 如果匹配成功，将这两个图标加入已匹配列表
        matched_icons.extend(clicks)
        score += 10  # 匹配成功得分
        undo_last_match = clicks.copy()  # 保存这次匹配用于撤销
        match_sound.play()  # 播放成功音效
    else:
        # 不匹配时，稍等一会再取消选中
        time.sleep(0.5)
        failure_sound.play()  # 播放失败音效

    # 清空已点击的图标
    clicks = []

def use_hint():
    """使用提示功能，随机提示一个未匹配的图标"""
    global hint_index, hint_used
    unmatched = [i for i in range(len(selected_icons)) if i not in matched_icons]
    if unmatched:
        hint_index = random.choice(unmatched)
        hint_used += 1

def undo():
    """撤销上一次匹配"""
    global matched_icons, undo_used, undo_last_match
    if undo_last_match:
        for icon in undo_last_match:
            matched_icons.remove(icon)  # 从匹配列表中移除撤销的图标
        undo_last_match = []  # 清空撤销记录
        undo_used = True

def handle_game_over():
    """处理游戏结束的逻辑"""
    global game_result, game_over

    # 判断游戏胜负
    if len(matched_icons) == len(selected_icons):
        game_result = "恭喜，你赢了！"
        success_sound.play()  # 播放胜利音效
    else:
        game_result = "时间到，你输了！"
        failure_sound.play()  # 播放失败音效

    game_over = True

# 绘制带白色底纹和灰色边框的文本
def draw_text_with_bg(text, font, color, bg_color, border_color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    pygame.draw.rect(screen, bg_color, text_rect)  # 白色底纹
    pygame.draw.rect(screen, border_color, text_rect, 2)  # 灰色边框
    screen.blit(text_surface, text_rect)

# 函数：绘制菜单页面
def draw_menu():
    screen.blit(menu_bg, (0, 0))  # 绘制菜单背景
    title = font_large.render("-动了个物小游戏-", True, (0, 0, 0))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    # 添加白色底纹和灰色边框的难度选择
    draw_text_with_bg("<1. 简单>", font_medium, (0, 0, 0), (255, 255, 255), (128, 128, 128), SCREEN_WIDTH // 2 - 100, 150)
    draw_text_with_bg("<2. 一般>", font_medium, (0, 0, 0), (255, 255, 255), (128, 128, 128), SCREEN_WIDTH // 2 - 100, 250)
    draw_text_with_bg("<3. 困难>", font_medium, (0, 0, 0), (255, 255, 255), (128, 128, 128), SCREEN_WIDTH // 2 - 100, 350)
    draw_text_with_bg("<4. 游戏说明>", font_medium, (0, 0, 0), (255, 255, 255), (128, 128, 128), SCREEN_WIDTH // 2 - 100, 450)

    pygame.display.flip()

# 函数：绘制帮助页面（游戏说明）
def draw_help():
    screen.blit(menu_bg, (0, 0))  # 使用菜单背景
    title = font_large.render("游戏说明", True, (0, 0, 0))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    # 游戏说明内容
    help_texts = [
        "1. 选择两张相同的图标来消除它们。",
        "2. 倒计时结束前，匹配所有图标即胜利。",
        "3. 按下 Ctrl+H 键可以使用提示功能。",
        "4. 按下 Ctrl+U 键可以撤销上一次匹配。",
    ]
    for i, text in enumerate(help_texts):
        draw_text_with_bg(text, font_small, (0, 0, 0), (255, 255, 255), (128, 128, 128), 100, 150 + i * 60)

    return_menu_text = font_medium.render("按任意键返回菜单", True, (0, 0, 0))
    screen.blit(return_menu_text, (SCREEN_WIDTH // 2 - return_menu_text.get_width() // 2, SCREEN_HEIGHT - 100))

    pygame.display.flip()

# 函数：绘制游戏页面
# 函数：绘制游戏页面
def draw_game():
    # 绘制左侧的游戏背景
    screen.blit(game_bg, (0, 0))

    # 绘制右侧的垃圾槽背景
    garbage_bin_x = SCREEN_WIDTH // 2
    garbage_bin_y = 0
    screen.blit(garbage_bin_bg, (garbage_bin_x, garbage_bin_y))

    # 添加“待匹配”文字，灰色底纹，黑色边框
    draw_text_with_bg("待匹配", font_medium, (0, 0, 0), (200, 200, 200), (0, 0, 0), 10, 10)

    # 添加“已匹配”文字，灰色底纹，黑色边框
    draw_text_with_bg("已匹配", font_medium, (0, 0, 0), (200, 200, 200), (0, 0, 0), garbage_bin_x + 10, 10)

    # 显示未匹配的图标，整齐排列在左侧游戏区域
    for i, icon in enumerate(selected_icons):
        x, y = icon_positions[i]
        if i in clicks:  # 给选中的图标加红色边框
            pygame.draw.rect(screen, (255, 0, 0), (x - 2, y - 2, icon_size[0] + 4, icon_size[1] + 4), 3)
        if i == hint_index:  # 提示的图标加绿色边框
            pygame.draw.rect(screen, (0, 255, 0), (x - 2, y - 2, icon_size[0] + 4, icon_size[1] + 4), 3)
        if i not in matched_icons:  # 如果图标未匹配成功，则在固定位置显示
            screen.blit(icon, (x, y))

    # 显示已匹配的图标，整齐排列在右侧垃圾槽区域
    cols = (ICON_PAIRS[difficulty] * 2) // 4  # 垃圾槽区域4行排列
    for j, icon in enumerate(matched_icons):
        matched_icon = selected_icons[icon]
        x = garbage_bin_x + (j % cols) * (icon_size[0] + 20)
        y = (j // cols) * (icon_size[1] + 20) + 50
        screen.blit(matched_icon, (x, y))

    # 显示剩余时间和分数，带白色底纹和灰色边框
    draw_text_with_bg(f"剩余时间: {max(0, time_left)} 秒", font_medium, (0, 0, 0), (255, 255, 255), (128, 128, 128), 10, SCREEN_HEIGHT - 100)
    draw_text_with_bg(f"得分: {score}", font_medium, (0, 0, 0), (255, 255, 255), (128, 128, 128), SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)

    pygame.display.flip()

# 函数：绘制结果页面
def draw_result():
    screen.blit(finished_bg, (0, 0))  # 使用结算背景
    draw_text_with_bg(game_result, font_large, (0, 0, 0), (255, 255, 255), (128, 128, 128), SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100)
    draw_text_with_bg("按任意键返回菜单", font_medium, (0, 0, 0), (255, 255, 255), (128, 128, 128), SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50)

    pygame.display.flip()

# 函数：主循环
def main_loop():
    global game_state, difficulty, score, time_left, selected_icons, matched_icons, icon_positions, hint_used, undo_used, start_time, game_over

    clock = pygame.time.Clock()
    running = True

    # 播放背景音乐
    pygame.mixer.music.play(-1)

    while running:
        screen.fill((255, 255, 255))
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_state == MENU:
                    if event.key == pygame.K_1:
                        difficulty = EASY
                        game_state = GAME
                    elif event.key == pygame.K_2:
                        difficulty = MEDIUM
                        game_state = GAME
                    elif event.key == pygame.K_3:
                        difficulty = HARD
                        game_state = GAME
                    elif event.key == pygame.K_4:  # 选择查看游戏说明
                        game_state = HELP
                    # 初始化游戏状态
                    if game_state == GAME:
                        score = 0
                        matched_icons = []
                        selected_icons = shuffle_icons()
                        icon_positions = generate_icon_positions()  # 生成图标的固定位置
                        start_time = time.time()
                        time_left = TIME_LIMIT[difficulty]
                        game_over = False
                elif game_state == HELP:  # 从帮助页面返回菜单
                    game_state = MENU
                elif game_state == RESULT:  # 在结果页面按任意键返回菜单
                    game_state = MENU
                elif event.key == pygame.K_h:  # 提示功能，按 H 键触发
                    use_hint()
                elif event.key == pygame.K_u:  # 撤销功能，按 U 键触发
                    undo()

            if event.type == pygame.MOUSEBUTTONDOWN and game_state == GAME:
                if not game_over:
                    handle_click(event.pos)

        # 更新游戏状态
        if game_state == MENU:
            draw_menu()
        elif game_state == HELP:
            draw_help()
        elif game_state == GAME:
            time_left = TIME_LIMIT[difficulty] - int(current_time - start_time)
            if time_left <= 0 or len(matched_icons) == len(selected_icons):
                game_over = True
                handle_game_over()
                game_state = RESULT
            else:
                draw_game()
        elif game_state == RESULT:
            draw_result()

        pygame.display.update()
        clock.tick(30)

    pygame.quit()

# 启动游戏
main_loop()