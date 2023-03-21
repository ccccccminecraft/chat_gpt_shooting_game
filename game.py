import pygame
import random
import sys  # 追加する

# 初期設定
pygame.init()
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2D Shooting Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
player_image = pygame.image.load("player.png")
enemy_image = pygame.image.load("enemy.png")
bullet_image = pygame.image.load("bullet.png")
game_state = "title"

# クラスの定義
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.last_shot_time = pygame.time.get_ticks()
        self.bullet_group = pygame.sprite.Group()

    def update(self):
        # 上下左右の移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        elif keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        elif keys[pygame.K_d]:
            self.rect.x += self.speed

        # 弾の発射
        if keys[pygame.K_LSHIFT]:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time >= 100:
                self.last_shot_time = now
                self.bullet_group.add(Bullet(self.rect.centerx, self.rect.top))
                # 弾の速度をプレイヤーの4倍に設定
                for bullet in self.bullet_group:
                    bullet.speed = -self.speed * 4

        # 画面外に出ないように調整
        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x > screen_width - self.rect.width:
            self.rect.x = screen_width - self.rect.width
        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y > screen_height - self.rect.height:
            self.rect.y = screen_height - self.rect.height

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(1, 5)

    def update(self):
        # 下方向に移動
        self.rect.y += self.speed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -20

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


# グループの定義
all_sprites_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()  # 追加する

# オブジェクトの生成
player = Player(screen_width / 2 - 32, screen_height - 64)
all_sprites_group.add(player)
player_group.add(player)

# メインループ
last_countdown_tick = pygame.time.get_ticks()
n = 20
spawn_countdown = 0
while True:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # ゲームステートに応じた処理
    if game_state == "title":
        screen.fill((0, 0, 0))
        title_text = font.render("2D Shooting Game", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width / 2, screen_height / 2 - 50))
        screen.blit(title_text, title_rect)
        start_text = font.render("Press SPACE to start", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=(screen_width / 2, screen_height / 2 + 50))
        screen.blit(start_text, start_rect)
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            game_state = "play"
            # オブジェクトの生成
            player = Player(screen_width / 2 - 32, screen_height - 64)
            all_sprites_group.add(player)
            player_group.add(player)
            pygame.time.set_timer(pygame.USEREVENT, 1000)
    elif game_state == "play":
        # オブジェクトの更新
        all_sprites_group.update()
        bullet_group.update()

        # 衝突判定
        for enemy in pygame.sprite.spritecollide(player, enemy_group, True):
            game_state = "gameover"
        for bullet in pygame.sprite.groupcollide(bullet_group, enemy_group, True, True).keys():
            pass

        # オブジェクトの描画
        screen.fill((0, 0, 0))
        all_sprites_group.draw(screen)

    elif game_state == "gameover":
        screen.fill((0, 0, 0))
        gameover_text = font.render("Game Over", True, (255, 255, 255))
        gameover_rect = gameover_text.get_rect(center=(screen_width / 2, screen_height / 2 - 50))
        screen.blit(gameover_text, gameover_rect)
        restart_text = font.render("Press SPACE to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 50))
        screen.blit(restart_text, restart_rect)
        n = 20
        spawn_countdown = 0
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            game_state = "title"
            all_sprites_group.empty()
            enemy_group.empty()
            bullet_group.empty()

    # 敵の生成
    now = pygame.time.get_ticks()
    if game_state == "play" and now:
        if now % 40 == 0:
            if n > 1:
                n -= 1
        last_countdown_tick = now

        spawn_countdown -= 1
        if spawn_countdown <= 0:
            spawn_countdown = n
            enemy = Enemy()
            all_sprites_group.add(enemy)
            enemy_group.add(enemy)

    # 画面の更新
    pygame.display.update()
    clock.tick(60)
