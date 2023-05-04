import random

import pygame
import pygame_menu
import csv
from model import Player, Enemy, WeaponBonus, Weapon, ShotgunBullet, HpBonus, PowerBlastBonus

difficulty = 1

screen = None
FPS = 60
WIDTH = 1200
HEIGHT = 800

player_name = 'John Doe'
finally_menu = None
score = 0

score_table = []

revolver = ['revolver', 500, 2000, 6, 10]
machine_gun = ['machine_gun', 100, 3000, 50, 5]


def start_game():
    severeness = 1
    clock = pygame.time.Clock()
    clock.tick(FPS)

    all_sprites = pygame.sprite.Group()
    mobs = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)

    is_shoot = False
    point_to_shoot = None

    font = pygame.font.Font(None, 36)

    bg_images = [None,
                 pygame.image.load("data/desert-bg.png").convert_alpha(),
                 pygame.image.load("data/ice-bg.png").convert_alpha(),
                 pygame.image.load("data/mars-bg.png").convert_alpha()
                 ]
    bg = bg_images[difficulty]
    # Делаем толпу противников
    for i in range(8):
        mob = Enemy(difficulty, severeness)
        all_sprites.add(mob)
        mobs.add(mob)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_shoot = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_shoot = False
            if event.type == pygame.MOUSEMOTION:
                player.rotate(event.pos[0], event.pos[1])
                point_to_shoot = event.pos
        if is_shoot and point_to_shoot:
            bull = player.shoot(point_to_shoot[0], point_to_shoot[1])
            if bull:
                if type(bull) == ShotgunBullet:
                    for i in bull.list_of_bullet:
                        bullets.add(i)
                        all_sprites.add(i)
                else:
                    bullets.add(bull)
                    all_sprites.add(bull)
        # враги бегут за игроком
        for i in mobs:
            i.set_speed(player.rect.centerx, player.rect.centery)

        # враги трогают игрока
        hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
        if hits:
            for hit in hits:
                hit.kick(player)

        # Игрок поднял бонус
        hits_bonus = pygame.sprite.spritecollide(player, bonuses, True, pygame.sprite.collide_circle)
        for hit in hits_bonus:
            if type(hit) == WeaponBonus:
                player.weapon = Weapon(*hit.weapon)
            elif type(hit) == HpBonus:
                player.hp = 100
            elif type(hit) == PowerBlastBonus:
                list_of_bullet = hit.shoot()
                for i in list_of_bullet:
                    bullets.add(i)
                    all_sprites.add(i)

        # снаряд попал во врага
        hits_bullet = pygame.sprite.groupcollide(mobs, bullets, False, True, pygame.sprite.collide_circle)
        for hit in hits_bullet:
            player.score += 10
            hit.hp -= player.weapon.damage

            # 10% что из врага выпадет бонус
            if hit.hp <= 0:
                if random.randint(0, 3) == 0:
                    type_of_bonus = random.choice([WeaponBonus, HpBonus, PowerBlastBonus])

                    bonus = type_of_bonus(hit.rect.centerx, hit.rect.centery)
                    bonuses.add(bonus)
                    all_sprites.add(bonus)
                hit.kill()
                m = Enemy(difficulty, severeness)
                all_sprites.add(m)
                mobs.add(m)

        # Обновление и отрисовка текста
        screen.blit(bg, (0, 0))
        all_sprites.update()
        ammo = font.render(str(player.weapon.cur_cage), True, (255, 255, 255))
        hp = font.render(str(player.hp), True, (0, 255, 0))
        score = font.render(f'Score: {player.score}', True, (255, 255, 255))
        screen.blit(hp, (player.rect.x + 20, player.rect.y - 20))
        screen.blit(ammo, (player.rect.x - 20, player.rect.y - 20))
        screen.blit(score, (0, 0))
        clock.tick(FPS)
        all_sprites.draw(screen)

        screen.blit(player.image1, player.rect)
        pygame.display.update()

        severeness = (player.score // 1000)/10 + 1
        if len(mobs) < 8 * severeness:
            m = Enemy(difficulty, severeness)
            all_sprites.add(m)
            mobs.add(m)
        if player.hp <= 0:
            run = False

        pygame.display.flip()

    finally_screen(player.score)


def score_table_show():
    global score_table
    score_table = []
    score_menu = pygame_menu.Menu(f'Самые крутые', 600, 500, theme=pygame_menu.themes.THEME_GREEN)
    score_table = csv_reader()
    score_table.sort(key=lambda x: int(x['score']), reverse=True)
    score_table = score_table[:min([len(score_table), 5])]
    for score in range(len(score_table)):
        score_menu.add.label(f'{score + 1}. {score_table[score]["name"]} - {score_table[score]["score"]}')
    score_menu.add.button('В меню', score_menu.disable)
    score_menu.mainloop(screen)


# финальное окно
def finally_screen(cur_score):
    global player_name, finally_menu, score
    score = cur_score
    finally_menu = pygame_menu.Menu(f'Вот и все! Ваши очки: {score}', 600, 500, theme=pygame_menu.themes.THEME_DARK)
    finally_menu.add.text_input('Введите имя :', default='John Doe', onchange=fin_menu_player_name_onchange)
    finally_menu.add.button('В меню', fin_menu_close)
    finally_menu.mainloop(screen)


# выбор уровня
def set_difficulty(value, dif):
    global difficulty
    difficulty = dif
    print(f'Сложность изменена на {difficulty}')


# ввод имени игрока
def fin_menu_player_name_onchange(name):
    global player_name
    player_name = name


# закрытие финального окна и запись в csv
def fin_menu_close():
    global finally_menu
    finally_menu.disable()
    csv_writer()


def csv_writer():
    with open('data/scores.csv', 'a', encoding="utf8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['name', 'score'])
        writer.writerow({'name': player_name, 'score': score})
        csvfile.close()


def csv_reader():
    global score_table
    try:
        with open('data/scores.csv', 'r', encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['name', 'score'])
            for r in reader:
                score_table.append(r)
        return score_table
    except:
        return []


if __name__ == '__main__':
    pygame.init()
    size = width, height = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)
    menu = pygame_menu.Menu('Welcome', 600, 500, theme=pygame_menu.themes.THEME_BLUE)
    menu.add.selector('Выберите уровень:', [('1', 1), ('2', 2), ('3', 3)], onchange=set_difficulty)
    menu.add.button('Старт!', start_game)
    menu.add.button('Таблица рекордов', score_table_show)
    menu.add.button('Выход', pygame_menu.events.EXIT)
    menu.mainloop(screen)
