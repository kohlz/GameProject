import pygame
import os
import random
import time

# 初始化Pygame
pygame.init()

# 初始化垃圾类(垃圾袋)
class Garbage(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.visible = True

    def clear(self):
        # 移除垃圾图片
        map_image.blit(map_image, self.rect, self.rect)  # 用地图图片覆盖垃圾区域
        self.visible = False  # 将垃圾设置为不可见
        self.kill()  # 删除垃圾对象

# 初始化种植物
class Grass(pygame.sprite.Sprite):
    def __init__(self, image, position):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.visible = True

# 创建目标
trash_clean = 0
grass_plant = 0

# 设置窗口尺寸
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# 设置帧率
FPS = 60

# 设置颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 加载地图和人物图片
# 将默认人物替换成面向玩家
map_image = pygame.image.load(os.path.join('images', 'map.png'))
player_image = pygame.image.load(os.path.join('images', 'front_player.png'))

# 初始化地图草块数组
map_width = map_image.get_width()
map_height = map_image.get_height()
grass_block_size = 40
grass_blocks = [[None for _ in range(map_image.get_width() // 40)] for _ in range(map_image.get_height() // 40)]

# 加载草图片
new_grass_image = pygame.image.load(os.path.join('images', 'newgrass.png'))

# 放大人物图片
scaled_width = 18  # 放大后的宽度
scaled_height = 30  # 放大后的高度
player_image = pygame.transform.scale(player_image, (scaled_width, scaled_height))

# 获取人物图片的矩形区域
player_rect = player_image.get_rect()

# 设置人物初始位置
player_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

# 设置人物速度
player_speed = 3

# 创建窗口
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Environment')

# 创建字体对象
font = pygame.font.Font(None, 16)

# 游戏主循环条件
running = True
clock = pygame.time.Clock()

# 创建垃圾对象列表
garbage_list = []

# 创建随机垃圾类型
garbage_type = ['cans.png', 'plasticbag.png', 'trashbag.png']

# 创建垃圾总是
garbage_num = 20

# 创建随机垃圾图片函数
def randomGarbageImage():
    return garbage_type[random.randint(0, 2)]

# 在地图上随机放置多个垃圾（生成，不是绘制）
for _ in range(garbage_num):  # 生成若干个垃圾
    garbage_image = pygame.image.load(os.path.join('images', randomGarbageImage()))
    while True:
        x = random.randint(0, WINDOW_WIDTH - 40 - garbage_image.get_width())  # 随机生成x坐标
        y = random.randint(0, WINDOW_HEIGHT - 40 - garbage_image.get_height())  # 随机生成y坐标
        rect = pygame.Rect(x, y, garbage_image.get_width(), garbage_image.get_height())
        overlapping = False
        for garbage in garbage_list:
            if rect.colliderect(garbage.rect):
                overlapping = True
                break
        if not overlapping:
            break
    garbage = Garbage(garbage_image, (x, y))
    garbage_list.append(garbage)

# 检测玩家是否站在垃圾上，并检查该垃圾是否被清除
def checkPlayerGarbagePosition():
    for garbage in garbage_list:
        if player_rect.colliderect(garbage.rect) and garbage.visible:
            return True
    return False

# 加载玩家不同方向的图片
player_up_image = pygame.image.load(os.path.join('images', 'back_player.png'))
player_down_image = pygame.image.load(os.path.join('images', 'front_player.png'))
player_left_image = pygame.image.load(os.path.join('images', 'left_player.png'))
player_right_image = pygame.image.load(os.path.join('images', 'right_player.png'))

#放大玩家图片
player_up_image = pygame.transform.scale(player_up_image, (scaled_width, scaled_height))
player_down_image = pygame.transform.scale(player_down_image, (scaled_width, scaled_height))
player_left_image = pygame.transform.scale(player_left_image, (12, scaled_height))
player_right_image = pygame.transform.scale(player_right_image, (12, scaled_height))

# 设置地图边界
map_boundary = pygame.Rect(0, 0, map_image.get_width(), map_image.get_height())

# 检查玩家是否可以种植草块
def can_plant_grass(player_rect):
    player_block_x = player_rect.left // grass_block_size
    player_block_y = player_rect.top // grass_block_size
    # 检查玩家所在的草块是否已经被占据
    if grass_blocks[player_block_y][player_block_x]:
        return False
    
    # 检查玩家是否站在垃圾上
    for garbage in garbage_list:
        garbage_block_x = garbage.rect.left // grass_block_size
        garbage_block_y = garbage.rect.top // grass_block_size
        if player_block_x == garbage_block_x and player_block_y == garbage_block_y and garbage.visible == True:
            return False
    
    return True

# 在玩家位置种植草块
def plant_grass(player_rect):
    i = player_rect.top // grass_block_size
    j = player_rect.left // grass_block_size
    grass_image= new_grass_image
    grass_blocks[i][j] = Grass(grass_image, (j * grass_block_size, i * grass_block_size))

# 初始化倒计时器
start_time = time.time()  # 记录游戏开始时间
spawn_interval = 10  # 生成垃圾的时间间隔（秒）
next_spawn_time = start_time + spawn_interval  # 下一个垃圾生成时间

# 教程部分
initial_startup = True

# 失败条件
spawn_garbage_count = 0

# 添加声音文件
grass_plant_audio = pygame.mixer.Sound(os.path.join('audio', 'grass.mp3'))
garbage_clean_audio = pygame.mixer.Sound(os.path.join('audio', 'garbage.mp3'))

while running:
    window.fill(WHITE)

    # 绘制地图
    window.blit(map_image, (0, 0))
    
    # 游戏开始时显示教程
    if initial_startup:
        dialog_text = (
        "Welcome!",
        "Play this game to help saving our natural environment",
        "You need to try your best to reach the target before 20 garbage spawn",
        "Press WASD to move",
        "Press 'space' to clean up trash",
        "Press 'f' to plant grass",
        "Your goal: Plant 100 grass and clean up 20 trash",
        "Press 'y' to play this game!"
        )
        
        # 计算对话框的行数和高度
        line_height = 30
        dialog_height = len(dialog_text) * line_height

        # 计算对话框的位置和大小
        dialog_width = 600
        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

        # 绘制对话框背景
        pygame.draw.rect(window, (255, 255, 255), dialog_rect)  # 绘制对话框背景
        pygame.draw.rect(window, (0, 0, 0), dialog_rect, 2)  # 绘制对话框边框

        # 绘制对话框文本
        font = pygame.font.Font(None, 24)
        text_y = dialog_rect.top + 20  # 设置文本的起始 Y 坐标
        for line in dialog_text:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(dialog_rect.centerx, text_y))
            window.blit(text_surface, text_rect)
            text_y += line_height  # 逐行增加 Y 坐标，以控制文本的行距
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    initial_startup = False
                    
    elif spawn_garbage_count == 20:
        dialog_text = (
        "You didn't reach the target",
        "Unfortunately, you lost the game",
        "Press 'Space' to quit the game"
        )
        
        # 计算对话框的行数和高度
        line_height = 30
        dialog_height = len(dialog_text) * line_height

        # 计算对话框的位置和大小
        dialog_width = 600
        dialog_x = (WINDOW_WIDTH - dialog_width) // 2
        dialog_y = (WINDOW_HEIGHT - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

        # 绘制对话框背景
        pygame.draw.rect(window, (255, 255, 255), dialog_rect)  # 绘制对话框背景
        pygame.draw.rect(window, (0, 0, 0), dialog_rect, 2)  # 绘制对话框边框

        # 绘制对话框文本
        font = pygame.font.Font(None, 24)
        text_y = dialog_rect.top + 20  # 设置文本的起始 Y 坐标
        for line in dialog_text:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(dialog_rect.centerx, text_y))
            window.blit(text_surface, text_rect)
            text_y += line_height  # 逐行增加 Y 坐标，以控制文本的行距
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False  # 用户按下空格键时退出程序
    
    # 游戏结束时显示对话框
    elif grass_plant >= 80 and trash_clean >= 20:
        # 绘制对话框背景
        dialog_rect = pygame.Rect(200, 200, 400, 200)
        pygame.draw.rect(window, (255, 255, 255), dialog_rect)  # 绘制对话框背景
        pygame.draw.rect(window, (0, 0, 0), dialog_rect, 2)  # 绘制对话框边框

        dialog_text = (
        "Game Over!",
        "Thanks for Protecting the Environment!",
        "Remember to clean up the rubbish!",
        "Press 'Space' to quit game"
        )
        
        # 绘制对话框文本
        font = pygame.font.Font(None, 24)
        text_y = dialog_rect.top + 20  # 设置文本的起始 Y 坐标
        for line in dialog_text:
            text_surface = font.render(line, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(dialog_rect.centerx, text_y))
            window.blit(text_surface, text_rect)
            text_y += 30  # 逐行增加 Y 坐标，以控制文本的行距
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False  # 用户按下空格键时退出程序
    
    else:
        # 检测玩家是否站在垃圾上方，如果是则显示对话框
        if checkPlayerGarbagePosition():
            dialog_width = 160  # 对话框宽度
            dialog_height = 30  # 对话框高度
            dialog_rect = pygame.Rect(player_rect.centerx - dialog_width // 2, player_rect.top - dialog_height, dialog_width, dialog_height)  # 将对话框移动至玩家头顶
            pygame.draw.rect(window, WHITE, dialog_rect)  # 设置为白色
            pygame.draw.rect(window, BLACK, dialog_rect, 2)  # 添加边框
            dialog_text = font.render("Here is an Rubbish!", True, BLACK)  # 添加文字
            window.blit(dialog_text, (player_rect.centerx - dialog_text.get_width() // 2, player_rect.top - dialog_height + 5))
        
        # 绘制垃圾
        for garbage in garbage_list:
            if garbage.visible:
                window.blit(garbage.image, garbage.rect)
                
        # 绘制草块
        for row in grass_blocks:
            for grass in row:
                if grass:
                    window.blit(grass.image, grass.rect)

        # 绘制玩家
        window.blit(player_image, player_rect)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # 当按下空格键时，判断玩家是否与垃圾重叠，如果是则清除垃圾
                if event.key == pygame.K_SPACE:
                    for garbage in garbage_list:
                        if player_rect.colliderect(garbage.rect):
                            garbage.clear()
                            trash_clean += 1
                            garbage_clean_audio.play()
                # 当按下键盘上的F键时，检查玩家是否能够种植草块，并在合适的情况下进行种植
                if event.key == pygame.K_f:
                    if can_plant_grass(player_rect):
                        plant_grass(player_rect)
                        grass_plant += 1
                        grass_plant_audio.play()
            
                        
        # 获取键盘按键状态
        keys = pygame.key.get_pressed()
 
        # 根据按键状态移动人物
        # 更新人物图片
        if keys[pygame.K_a] and player_rect.left > map_boundary.left:
            player_image = player_left_image
            player_rect.x -= player_speed
        if keys[pygame.K_d] and player_rect.left < map_boundary.right - 40:
            player_image = player_right_image
            player_rect.x += player_speed
        if keys[pygame.K_w] and player_rect.top > map_boundary.top:
            player_image = player_up_image
            player_rect.y -= player_speed
        if keys[pygame.K_s] and player_rect.top < map_boundary.bottom - 40:
            player_image = player_down_image
            player_rect.y += player_speed

        # 计算已经过去的时间
        current_time = time.time()
        time_elapsed = current_time - start_time
        
        # 检查是否达到生成垃圾的时间
        if current_time >= next_spawn_time:
            garbage_image = pygame.image.load(os.path.join('images', randomGarbageImage()))
            while True:
                x = random.randint(0, WINDOW_WIDTH - 40 - garbage_image.get_width())  # 随机生成x坐标
                y = random.randint(0, WINDOW_HEIGHT - 40 - garbage_image.get_height())  # 随机生成y坐标
                rect = pygame.Rect(x, y, garbage_image.get_width(), garbage_image.get_height())
                overlapping = False
                # 检查垃圾是否与草块重叠
                for row in grass_blocks:
                    for grass in row:
                        if grass and rect.colliderect(grass.rect):
                            overlapping = True
                            break
                    if overlapping:
                        break
                if not overlapping:
                    break
            garbage = Garbage(garbage_image, (x, y))
            garbage_list.append(garbage)  
            spawn_garbage_count += 1  

            # 更新下一个垃圾生成时间
            next_spawn_time = current_time + spawn_interval

        time_until_spawn = next_spawn_time - current_time  # 计算剩余时间
        
        # 绘制倒计时文本
        font_timer = pygame.font.Font(None, 36)
        text = font_timer.render(f"Next garbage spawn in: {int(time_until_spawn)} seconds", True, BLACK)
        window.blit(text, (10, 10))
        
        # 玩家草方块/垃圾信息
        grass_garbage_text = font_timer.render(f"Grass used: {grass_plant}/80   Garbage cleared: {trash_clean}/20   Garbage spawn: {spawn_garbage_count}/20", True, BLACK)
        window.blit(grass_garbage_text, (10, 50))
    
    # 更新屏幕
    pygame.display.flip()

    # 控制帧率
    clock.tick(FPS)

# 退出Pygame
pygame.quit()