import os
import sqlite3
import uuid
from flask import Flask, render_template, abort, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
app = Flask(__name__)
app.secret_key = 'ue5_sqlite_secret_key_very_long_and_random'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

# Настройка папки для загрузки картинок
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- ПОЛНЫЕ ДАННЫЕ ДЛЯ НАПОЛНЕНИЯ БАЗЫ ---
GAMES_DATA = [
    ("S.T.A.L.K.E.R. 2: Heart of Chornobyl", "Unreal Engine 5", "FPS / Survival",
     "Технический пример: Использование Nanite для ультра-детализированной растительности и мусора. Lumen обеспечивает честное освещение в темных туннелях без запекания.",
     "https://store.steampowered.com/app/1643320/STALKER_2_Heart_of_Chornobyl/",
     "https://store.epicgames.com/ru/p/stalker-2-heart-of-chornobyl"),

    ("Black Myth: Wukong", "Unreal Engine 5", "Action-RPG",
     "Технический пример: Референс по созданию сложной шерсти, системы частиц (Niagara) для магии и использованию микро-полигональной геометрии на персонажах.",
     "https://store.steampowered.com/app/2358720/Black_Myth_Wukong/",
     "https://store.epicgames.com/ru/p/black-myth-wukong-87a72b"),

    ("Fortnite", "Unreal Engine 5.1+", "Battle Royale",
     "Технический пример: Лучшая демонстрация World Partition (загрузка огромного мира частями) и физики разрушений Chaos Physics в мультиплеере.",
     None,
     "https://store.epicgames.com/ru/p/fortnite"),

    ("Hellblade II: Senua's Saga", "Unreal Engine 5", "Cinematic",
     "Технический пример: Эталон работы с MetaHuman Animator (лицевая анимация) и фотограмметрией Quixel Megascans.",
     "https://store.steampowered.com/app/2461850/Senuas_Saga_Hellblade_II/",
     None),

    ("Tekken 8", "Unreal Engine 5", "Fighting",
     "Технический пример: Демонстрация того, как движок справляется с тяжелыми эффектами частиц и динамическим светом на 60 FPS в замкнутых аренах.",
     "https://store.steampowered.com/app/1778820/TEKKEN_8/",
     None),

    ("Valorant", "Unreal Engine 4", "Tactical FPS",
     "Технический пример: Идеальный кейс оптимизации рендеринга (Forward Shading) и сетевого кода для работы на самых слабых ПК.",
     None,
     "https://store.epicgames.com/ru/p/valorant"),

    ("Hogwarts Legacy", "Unreal Engine 4", "Open World RPG",
     "Технический пример: Изучите реализацию стриминга уровней (бесшовный переход из замка в открытый мир) и систему магии через Niagara VFX.",
     "https://store.steampowered.com/app/990080/Hogwarts_Legacy/",
     "https://store.epicgames.com/ru/p/hogwarts-legacy")
]

CATEGORIES_DATA = [
    ("Must-Have Ассеты и Плагины", "assets"),
    ("Blueprint & C++ Архитектура", "code-arch"),
    ("Графика и Рендеринг (Nanite/Lumen)", "rendering"),
    ("Геймплейные Системы (GAS)", "gas")
]

GUIDES_DATA = [
    ("gas", "Gameplay Ability System (GAS)", "intro-to-gas",
     "Массивный фреймворк для RPG/MOBA. Репликация, Prediction, Attributes, Tags.",
     "Hardcore", "Architecture",
     """
     <h2>1. Глубокое погружение в архитектуру</h2>
     <p><strong>Gameplay Ability System (GAS)</strong> — это не просто плагин, а альтернативный способ программирования геймплея в Unreal Engine. Это стандарт для мультиплеерных игр (Fortnite, Paragon, Valorant), где важна надежность, защита от читеров и сложная логика взаимодействия эффектов.</p>
     <h3>Основные компоненты (The Big 4):</h3>
     <ul>
         <li><strong>Ability System Component (ASC):</strong> "Мозг" системы. Компонент, который вешается на Actor (обычно на PlayerState для персистентности или Character для мобов). Он хранит все атрибуты, теги и активные способности.</li>
         <li><strong>Gameplay Attributes (AttributeSet):</strong> Класс C++, определяющий числовые значения (Health, Mana, AttackPower). GAS защищает их от прямого изменения. Вы не пишете <code>Health -= 10</code>. Вы применяете "Эффект", который модифицирует атрибут.</li>
         <li><strong>Gameplay Effects (GE):</strong> Данные, описывающие <em>как</em> меняются атрибуты. Могут быть:
            <ul>
                <li><strong>Instant:</strong> Мгновенный урон (минус 10 HP).</li>
                <li><strong>Duration:</strong> Бафф на 10 секунд (+50 к скорости).</li>
                <li><strong>Infinite:</strong> Постоянный эффект (пассивка от брони), пока не снимешь.</li>
            </ul>
         </li>
         <li><strong>Gameplay Abilities (GA):</strong> Логика действия. Блюпринт или C++ класс, определяющий, что происходит, когда игрок нажал кнопку: проигрывание анимации (Montage), спаун снаряда, затрата маны.</li>
     </ul>
     <h2>2. Пример реализации: "Огненный Шар" (Fireball)</h2>
     <p>Давайте разберем пошагово, как создается сложный скилл, а не просто спаун актора.</p>
     <h3>Шаг A: Настройка Tags</h3>
     <p>GAS работает на тегах (Gameplay Tags). Мы создаем структуру тегов:</p>
     <ul>
         <li><code>Ability.Skill.Fireball</code> (Идентификатор скилла)</li>
         <li><code>Cooldown.Skill.Fireball</code> (Тег отката)</li>
         <li><code>State.Casting</code> (Тег, блокирующий движение)</li>
     </ul>
     <h3>Шаг B: Создание Gameplay Ability</h3>
     <p>Внутри класса <code>GA_Fireball</code>:</p>
     <ol>
         <li><strong>Activation:</strong> Игрок нажимает кнопку. GAS проверяет, хватает ли маны (через Cost GE) и нет ли тега кулдауна.</li>
         <li><strong>CommitAbility:</strong> Если всё ок, списывается мана и вешается кулдаун.</li>
         <li><strong>PlayMontageAndWait:</strong> Запускается асинхронная задача (Task) проигрывания анимации каста.</li>
         <li><strong>WaitGameplayEvent:</strong> Способность ждет события "ProjectileHit" (попадание).</li>
         <li><strong>ApplyGameplayEffectToTarget:</strong> Когда снаряд попал, мы применяем <code>GE_FireDamage</code> к врагу.</li>
     </ol>
     <h2>3. Сетевая магия: Prediction (Предсказание)</h2>
     <p>Самое сложное в мультиплеере — сделать так, чтобы игрок не чувствовал лагов. GAS использует <strong>Prediction</strong>:</p>
     <p>Когда клиент нажимает "Выстрел", он <em>не ждет</em> ответа сервера. Он сразу проигрывает анимацию и тратит ману визуально. Сервер параллельно делает то же самое. Если сервер решит, что выстрел был невозможен (чит или лаг), он пришлет <strong>Correction</strong>, и GAS сам "откатит" состояние клиента (вернет ману, прервет анимацию).</p>
     <h2>4. Подводные камни и Сложности</h2>
     <ul>
         <li><strong>Только C++ для Атрибутов:</strong> Вы не можете создать AttributeSet на Blueprints. Вам придется писать на C++ макросы для репликации переменных.</li>
         <li><strong>Сложность отладки:</strong> Чтобы понять, почему урон не прошел, нужно использовать команду <code>showdebug abilitysystem</code> и разбираться в куче текста на экране.</li>
         <li><strong>Overkill для синглплеера:</strong> Если вы делаете простую бродилку, GAS только усложнит вам жизнь.</li>
     </ul>
     """),

    ("assets", "Ultra Dynamic Sky (UDS)", "ultra-dynamic-sky",
     "Полная симуляция атмосферы. Volumetric Clouds, Aurora, Weather Replication.",
     "Beginner", "Environment",
     """
     <h2>1. Анатомия ассета</h2>
     <p><strong>Ultra Dynamic Sky</strong> — это массивный Blueprint-контроллер, который управляет десятками подсистем движка одновременно. Это не просто "небо", это менеджер рендеринга атмосферы.</p>
     <h3>Из чего он состоит внутри:</h3>
     <ul>
         <li><strong>Sky Atmosphere Component:</strong> Физически корректное рассеивание света (Рэлеевское и Ми). Определяет цвет неба в зависимости от положения солнца.</li>
         <li><strong>Volumetric Clouds:</strong> Объемные облака, использующие Raymarching. В UDS они настроены так, чтобы принимать тени от других облаков и отбрасывать тени на землю.</li>
         <li><strong>Exponential Height Fog:</strong> Туман, который меняет плотность и цвет в зависимости от погоды (синий утром, оранжевый на закате).</li>
         <li><strong>Sky Light with Real-Time Capture:</strong> UDS умеет перезахватывать освещение неба в реальном времени (тяжелая операция), чтобы тени в тенях были правильного цвета.</li>
     </ul>
     <h2>2. Система Погоды (Weather System)</h2>
     <p>Это самая мощная часть UDS. Она не просто включает дождь, она меняет свойства материалов во всей игре.</p>
     <h3>Как работает намокание (DLWE):</h3>
     <p>UDS использует <strong>Material Parameter Collection (MPC)</strong>. Когда начинается дождь:</p>
     <ol>
         <li>UDS плавно меняет переменную <code>Wetness</code> от 0 до 1 в глобальной коллекции.</li>
         <li>Все ваши материалы (земля, стены, асфальт), в которые вы добавили функцию <code>UDS_Weather_Integration</code>, читают эту переменную.</li>
         <li>Материалы меняют свои свойства: уменьшается <em>Roughness</em> (становятся блестящими), темнеет <em>Base Color</em> (эффект мокрой ткани) и добавляются нормали капель.</li>
     </ol>
     <h2>3. Производительность и Оптимизация</h2>
     <p>UDS очень красивый, но может "убить" FPS, если не настроить его правильно.</p>
     <ul>
         <li><strong>Облака (Volumetric Clouds):</strong> Самая дорогая часть. В настройках UDS есть пресеты качества. Для режима 60 FPS на консолях рекомендуется снижать Steps count.</li>
         <li><strong>Тени от облаков:</strong> Отключите <code>Cloud Shadows on Ground</code>, если у вас много растительности, иначе просчет теней станет слишком дорогим.</li>
         <li><strong>Sky Light Update Mode:</strong> Никогда не ставьте "Every Frame" для динамических сцен, если у вас нет мощного GPU. Используйте "Periodically" или умный режим, который обновляет свет только при резкой смене времени суток.</li>
     </ul>
     """),

    ("assets", "FluidNinja LIVE", "fluid-ninja",
     "GPU-симуляция флюидов. Navier-Stokes уравнения в реальном времени внутри материалов.",
     "Advanced", "VFX",
     """
     <h2>1. Техническая магия: Как это работает?</h2>
     <p>Обычно симуляция жидкости (вода, дым) — это задача для суперкомпьютеров или оффлайн-рендера (Houdini). <strong>FluidNinja LIVE</strong> делает это в реальном времени в игре. Как?</p>
     <p>Он решает упрощенные уравнения Навье-Стокса прямо в пиксельном шейдере. Он не создает миллионы частиц (CPU Particles). Вместо этого он использует каскад <strong>Render Targets</strong> (текстур, в которые можно писать).</p>
     <h3>Цикл симуляции (каждый кадр):</h3>
     <ol>
         <li><strong>Density Map:</strong> Где сейчас находится "вещество" (дым/огонь).</li>
         <li><strong>Velocity Map:</strong> Куда движется каждый пиксель вещества (векторное поле).</li>
         <li><strong>Pressure Solver:</strong> Вычисление давления, чтобы жидкость вела себя как несжимаемая среда (завихрения).</li>
         <li><strong>Advection:</strong> Перенос плотности по полю скоростей.</li>
     </ol>
     <p>Всё это происходит на GPU, поэтому процессор (CPU) остается свободным для игровой логики.</p>
     <h2>2. Интеграция с геймплеем</h2>
     <p>Самое крутое — это взаимодействие с миром.</p>
     <h3>Пример: Персонаж, идущий сквозь туман</h3>
     <p>Чтобы персонаж "разгонял" туман:</p>
     <ul>
         <li>К костям персонажа (руки, ноги) крепятся простые сферы или капсулы.</li>
         <li>Эти капсулы не видны в игре, но они рисуются в специальный буфер FluidNinja.</li>
         <li>FluidNinja читает этот буфер и добавляет векторы скорости в симуляцию в местах, где находятся капсулы.</li>
         <li>Результат: туман завихряется точно по траектории движения меча или ног.</li>
     </ul>
     <h2>3. Ограничения</h2>
     <ul>
         <li><strong>Это 2D симуляция:</strong> Несмотря на то, что она выглядит объемной (благодаря Raymarching шейдеру), физически она происходит на плоскости. Вы не сможете сделать полноценную 3D воду, которая наливается в стакан.</li>
         <li><strong>Память видеокарты (VRAM):</strong> FluidNinja использует много текстурной памяти для Render Targets. Будьте осторожны с разрешением (не ставьте 4K для лужи).</li>
     </ul>
     """),

    ("rendering", "Lumen Global Illumination", "lumen-gi",
     "Software Ray Tracing. Surface Cache, Voxel Lighting и ограничения технологии.",
     "Intermediate", "Lighting",
     """
     <h2>1. Технический разбор Lumen</h2>
     <p><strong>Lumen</strong> — это гибридная система трассировки лучей. Главная её фишка — она работает на консолях (PS5/Xbox) и видеокартах без RTX ядер (хотя с RTX работает лучше).</p>
     <h3>Как Lumen творит магию (Software Ray Tracing):</h3>
     <p>Вместо того чтобы трассировать лучи в реальную геометрию (которая может состоять из миллионов полигонов Nanite и убить любую видеокарту), Lumen использует упрощенное представление сцены.</p>
     <ol>
         <li><strong>Surface Cache (Кэш поверхностей):</strong> Lumen захватывает скриншоты ваших объектов со всех сторон и создает "карточки" (Cards) — упрощенные версии мешей.</li>
         <li><strong>Трассировка в кэш:</strong> Лучи света трассируются именно в эти "карточки", а не в реальные треугольники. Это в 100 раз быстрее.</li>
         <li><strong>Voxel Lighting:</strong> Для дальних объектов и грубого освещения Lumen использует воксельную структуру (как Minecraft, но невидимую).</li>
     </ol>
     <h2>2. Проблемы и Артефакты (Light Leaking)</h2>
     <p>Вы часто будете встречать "протечки" света (Light Leaks) в закрытых помещениях. Почему?</p>
     <ul>
         <li><strong>Тонкие стены:</strong> Поскольку Lumen использует упрощенные "карточки", стена толщиной в 10см может просто не попасть в Surface Cache, и свет пройдет сквозь неё. <strong>Решение:</strong> Делайте стены толще (минимум 20-40см) или используйте отдельные меши для стен и потолка.</li>
         <li><strong>Модульные меши:</strong> Если вы строите дом из кусков, Lumen может плохо освещать стыки.</li>
         <li><strong>Эмиссионные материалы:</strong> Lumen поддерживает свет от материалов (светящаяся лава), но только если объект достаточно большой. Маленькие яркие светодиоды не будут освещать комнату (они отсекутся оптимизацией).</li>
     </ul>
     <h2>3. Hardware Ray Tracing (HWRT)</h2>
     <p>Если в настройках проекта включить "Use Hardware Ray Tracing when available", Lumen начнет использовать реальные ядра RTX. Это даст:</p>
     <ul>
         <li>Более точные отражения (в зеркале будет видно реальное лицо персонажа, а не упрощенное).</li>
         <li>Отражения на полупрозрачных поверхностях.</li>
         <li>Но это стоит примерно 20-30% FPS.</li>
     </ul>
     """),

    ("rendering", "Nanite Geometry", "nanite-geo",
     "Кластерный рендеринг. VSM Shadows, Overdraw и работа с растительностью.",
     "Intermediate", "Optimization",
     """
     <h2>1. Как Nanite обманывает систему?</h2>
     <p>Традиционный пайплайн рендеринга захлебывается, когда на экране много мелких треугольников (меньше 1 пикселя). Видеокарта тратит ресурсы на их обработку, хотя визуально их не видно.</p>
     <p><strong>Nanite</strong> решает это, полностью меняя формат хранения мешей.</p>
     <h3>Структура данных:</h3>
     <ul>
         <li>Меш разбивается на группы треугольников — <strong>Кластеры</strong> (по 128 треугольников).</li>
         <li>Кластеры группируются в иерархию (дерево).</li>
         <li>В рантайме Nanite выбирает уровень детализации <em>для каждого кластера отдельно</em>, а не для всего объекта целиком.</li>
         <li>Это позволяет отрисовывать 10 миллиардов полигонов в кадре, сохраняя бюджет в ~10-20мс.</li>
     </ul>
     <h2>2. Virtual Shadow Maps (VSM)</h2>
     <p>Nanite работает в паре с <strong>VSM</strong>. Обычные карты теней (Shadow Maps) для геометрии такой сложности требовали бы гигабайты памяти. VSM разбивает карту теней на "плитки" (tiles) и обновляет только те плитки, где что-то изменилось или куда смотрит камера.</p>
     <p>Именно VSM дает те самые невероятно четкие тени от каждого листика на дереве.</p>
     <h2>3. Что нельзя делать с Nanite (пока что)</h2>
     <p>Несмотря на мощь, у Nanite есть ограничения:</p>
     <ul>
         <li><strong>Translucency / Masked:</strong> Nanite поддерживает прозрачность (например, траву или решетки), но это стоит дороже (Overdraw), чем обычная геометрия. Для густой травы иногда лучше использовать старый метод, если FPS проседает.</li>
         <li><strong>World Position Offset (WPO):</strong> Вы можете анимировать Nanite-деревья (ветер), но это требует пересчета кластеров каждый кадр. Слишком много анимированных Nanite-объектов могут перегрузить GPU.</li>
         <li><strong>Splines:</strong> Деформируемые сплайны (дороги) пока поддерживаются ограниченно.</li>
     </ul>
     """),

    ("code-arch", "Enhanced Input System", "enhanced-input",
     "Контекстно-зависимый ввод. Triggers, Modifiers и инъекция инпута.",
     "Beginner", "Input",
     """
     <h2>1. Философия: Контекст важнее кнопки</h2>
     <p>Главная идея <strong>Enhanced Input</strong>: "Игра не должна знать, какая кнопка нажата. Она должна знать, что <em>пользователь хочет сделать</em>".</p>
     <h3>Иерархия классов:</h3>
     <ul>
         <li><strong>Input Action (IA_Jump):</strong> Абстрактное намерение "Прыгнуть". Тип данных: Digital (bool).</li>
         <li><strong>Input Action (IA_Move):</strong> Намерение "Двигаться". Тип данных: Axis2D (Vector2D).</li>
         <li><strong>Input Mapping Context (IMC_Default):</strong> Таблица связей. "IA_Jump = Spacebar", "IA_Move = WASD".</li>
     </ul>
     <h2>2. Модификаторы (Modifiers)</h2>
     <p>Вам больше не нужно писать математику в коде для обработки сырых данных с джойстика.</p>
     <ul>
         <li><strong>Dead Zone:</strong> Автоматически игнорирует микро-движения дрейфующего стика.</li>
         <li><strong>Negate:</strong> Инвертирует ось (например, для оси Y при движении назад).</li>
         <li><strong>Swizzle Input Axis Values:</strong> Меняет местами X и Y (полезно, когда геймпад выдает данные не в том порядке, который нужен вашему персонажу).</li>
         <li><strong>Response Curve:</strong> Позволяет сделать прицеливание более точным (экспоненциальная кривая чувствительности).</li>
     </ul>
     <h2>3. Триггеры (Triggers)</h2>
     <p>Определяют, <em>когда</em> сработает событие. Очень мощный инструмент для комбо.</p>
     <ul>
         <li><strong>Hold:</strong> Событие сработает, только если держать кнопку N секунд (например, взаимодействие с сундуком).</li>
         <li><strong>Pulse:</strong> Срабатывает повторно каждые N секунд, пока кнопка зажата (автоматическая стрельба).</li>
         <li><strong>Chord Action:</strong> Самое вкусное. Действие срабатывает ТОЛЬКО если нажата другая кнопка. Пример: <code>IA_StrongAttack</code> срабатывает на ЛКМ, но только если в триггере указано "Requires IA_Shift".</li>
     </ul>
     <h2>4. Динамическая смена управления</h2>
     <p>В C++ или Blueprints вы можете делать так:</p>
     <pre style="background:#111; padding:10px; color:#8f8;">
// Игрок сел в машину
Subsystem->AddMappingContext(IMC_Car, Priority=1);
// Игрок открыл инвентарь
Subsystem->AddMappingContext(IMC_Menu, Priority=2); 
// (теперь WASD управляют курсором в меню, а не персонажем)</pre>
     """),

    ("code-arch", "Event Dispatchers (Delegates)", "blueprints-delegates",
     "Event-Driven Architecture. Single vs Multicast, Dynamic Delegates.",
     "Intermediate", "Blueprints",
     """
     <h2>1. Зачем это нужно? (Проблема спагетти-кода)</h2>
     <p>Новички часто делают так: в <code>BP_Player</code> пишут код: "Если HP < 0, получить виджет HUD, вызвать функцию ShowGameOver, найти всех врагов, сказать им StopAttacking".</p>
     <p>Это создает <strong>Hard References</strong>. Ваш персонаж загружает в память виджеты, врагов, музыку. Если вы удалите виджет — персонаж сломается.</p>
     <p><strong>Delegates (Event Dispatchers)</strong> решают это через принцип "Крик в пустоту". Персонаж просто кричит "Я УМЕР!", а все остальные сами решают, что делать.</p>
     <h2>2. Типы Делегатов в Unreal Engine</h2>
     <p>В C++ их много, в Blueprints они все спрятаны под названием Event Dispatcher, но внутри это работает так:</p>
     <h3>A. Single Delegate (Один получатель)</h3>
     <p>Используется для возврата значения. "Я поручаю тебе задачу, скажи мне, когда закончишь". Похоже на колбэк.</p>
     <h3>B. Multicast Delegate (Много получателей)</h3>
     <p>Это и есть Event Dispatcher в Блюпринтах.
     <br><strong>Пример:</strong> <code>OnQuestCompleted</code>.
     <br>Подписчики:</p>
     <ul>
         <li>UI (показать уведомление)</li>
         <li>SaveSystem (сохранить игру)</li>
         <li>XP Component (дать опыт)</li>
         <li>Sound Manager (проиграть джингл)</li>
     </ul>
     <p>Если убрать Sound Manager, код квеста не сломается. Он просто продолжит вещать в пустоту.</p>
     <h2>3. Dynamic Delegates</h2>
     <p>Это делегаты, которые можно сериализовать (сохранить) и вызывать по имени. Они медленнее обычных C++ делегатов, но именно они позволяют связывать события через Blueprints.</p>
     <h2>4. Практический пример: Интерактивная Дверь</h2>
     <ol>
         <li>Создаем <code>BP_Lever</code> (Рычаг). Добавляем Dispatcher <code>OnStateChanged(bool bIsOpen)</code>.</li>
         <li>Когда игрок нажимает E, рычаг проигрывает анимацию и вызывает <code>Call OnStateChanged</code>.</li>
         <li>На уровне ставим Рычаг и <code>BP_Door</code> (Дверь).</li>
         <li>В Level Blueprint (или через переменную Instance Editable) говорим: "Дверь, подпишись на событие этого Рычага".</li>
         <li><strong>Результат:</strong> Рычаг ничего не знает про дверь. Он может открывать дверь, включать свет или активировать ловушку. Один рычаг может активировать 10 дверей одновременно.</li>
     </ol>
     """)
]


# --- РАБОТА С БД ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        engine TEXT NOT NULL,
        genre TEXT NOT NULL,
        description TEXT NOT NULL,
        steam_url TEXT,
        epic_url TEXT
    );
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug_id TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS guides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_slug TEXT NOT NULL,
        title TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        tag TEXT NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (category_slug) REFERENCES categories (slug_id)
    );
    CREATE TABLE IF NOT EXISTS forum_threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        parent_type TEXT NOT NULL, 
        parent_id TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    ''')

    # Заполняем данные, только если таблицы пустые
    if cur.execute('SELECT count(*) FROM games').fetchone()[0] == 0:
        cur.executemany(
            'INSERT INTO games (title, engine, genre, description, steam_url, epic_url) VALUES (?, ?, ?, ?, ?, ?)',
            GAMES_DATA)
    if cur.execute('SELECT count(*) FROM categories').fetchone()[0] == 0:
        cur.executemany('INSERT INTO categories (name, slug_id) VALUES (?, ?)', CATEGORIES_DATA)
    if cur.execute('SELECT count(*) FROM guides').fetchone()[0] == 0:
        cur.executemany(
            'INSERT INTO guides (category_slug, title, slug, description, difficulty, tag, content) VALUES (?, ?, ?, ?, ?, ?, ?)',
            GUIDES_DATA)

    conn.commit()
    conn.close()


def get_db():
    # Timeout нужен, чтобы не крашилось, если DB Browser открыт
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# --- МАРШРУТЫ ---

@app.route('/')
def index():
    conn = get_db()
    try:
        cats = conn.execute('SELECT * FROM categories').fetchall()
    except sqlite3.OperationalError:
        conn.close()
        init_db()  # Пересоздаем, если таблиц нет
        return redirect(url_for('index'))

    final_categories = []
    for c in cats:
        guides = conn.execute('SELECT * FROM guides WHERE category_slug = ?', (c['slug_id'],)).fetchall()
        final_categories.append({"name": c['name'], "id": c['slug_id'], "guides": guides})
    conn.close()

    hero = {"title": "UE5 KNOWLEDGE BASE", "desc": "База знаний по Unreal Engine: архитектура и практики."}
    return render_template('index.html', hero=hero, categories=final_categories)


@app.route('/games')
def games():
    conn = get_db()
    games_list = conn.execute('SELECT * FROM games').fetchall()
    conn.close()
    return render_template('games.html', games=games_list)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/guide/<slug>')
def guide_page(slug):
    conn = get_db()
    guide = conn.execute('SELECT * FROM guides WHERE slug = ?', (slug,)).fetchone()
    if guide is None:
        conn.close()
        abort(404)
    comments = conn.execute(
        'SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.parent_type = "guide" AND c.parent_id = ? ORDER BY c.created_at DESC',
        (slug,)).fetchall()
    conn.close()
    return render_template('guide.html', guide=guide, comments=comments)


@app.route('/forum')
def forum():
    conn = get_db()
    threads = conn.execute(
        'SELECT t.*, u.username FROM forum_threads t JOIN users u ON t.user_id = u.id ORDER BY t.created_at DESC').fetchall()
    conn.close()
    return render_template('forum.html', threads=threads)


@app.route('/forum/create', methods=['GET', 'POST'])
def forum_create():
    if 'user_id' not in session: return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = get_db()
        try:
            conn.execute('INSERT INTO forum_threads (user_id, title, content, created_at) VALUES (?, ?, ?, ?)',
                         (session['user_id'], title, content, created_at))
            conn.commit()
            return redirect(url_for('forum'))
        except sqlite3.IntegrityError:
            session.clear()  # Сброс сессии, если юзера нет в базе
            return redirect(url_for('login'))
        finally:
            conn.close()
    return render_template('forum_create.html')


@app.route('/forum/<int:thread_id>')
def forum_thread(thread_id):
    conn = get_db()
    thread = conn.execute('SELECT t.*, u.username FROM forum_threads t JOIN users u ON t.user_id = u.id WHERE t.id = ?',
                          (thread_id,)).fetchone()
    if thread is None: conn.close(); abort(404)
    comments = conn.execute(
        'SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.parent_type = "thread" AND c.parent_id = ? ORDER BY c.created_at ASC',
        (str(thread_id),)).fetchall()
    conn.close()
    return render_template('forum_view.html', thread=thread, comments=comments)


# --- ЗАГРУЗКА КАРТИНОК (AJAX) ---
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'Empty filename'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in ['png', 'jpg', 'jpeg', 'gif', 'webp']: return jsonify({'error': 'Invalid file type'}), 400

    # Генерируем уникальное имя
    filename = str(uuid.uuid4()) + '.' + ext
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    return jsonify({'url': url_for('static', filename='uploads/' + filename)})


@app.route('/comment/<parent_type>/<parent_id>', methods=['POST'])
def add_comment(parent_type, parent_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    content = request.form['content'].strip()
    if content:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO comments (user_id, parent_type, parent_id, content, created_at) VALUES (?, ?, ?, ?, ?)',
                (session['user_id'], parent_type, parent_id, content, created_at))
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

    if parent_type == 'guide':
        return redirect(url_for('guide_page', slug=parent_id))
    elif parent_type == 'thread':
        return redirect(url_for('forum_thread', thread_id=parent_id))
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if not username or not email or not password:
            flash('Все поля обязательны', 'error');
            return redirect(url_for('register'))
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                         (username, email, generate_password_hash(password)))
            conn.commit()
            flash('Аккаунт создан!', 'success');
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь уже существует', 'error')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id'];
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Неверные данные', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)