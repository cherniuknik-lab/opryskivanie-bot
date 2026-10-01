import os
import math
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0") or 0)
DB_FILE = os.getenv("SPRAY_DB_FILE", "spray.db")
TZ = ZoneInfo("Europe/Kyiv")

flow = {}

# ---------------- КНОПКИ ----------------
BTN_NEW = "➕ Новая работа"
BTN_PLAN_JOB = "📋 Запланированное задание"
BTN_REPORTS = "📊 Итоги"
BTN_REFILL_HISTORY = "📚 История заправок"
BTN_CORRECT_LAST = "✏️ Исправить последнее"
BTN_DELETE_JOB = "🗑 Удалить работу"
BTN_CONFIRM_DELETE = "✅ Да, удалить"
BTN_CANCEL_DELETE = "❌ Отмена"
BTN_TODAY = "📆 За сегодня"
BTN_BY_DATE = "🔎 По дате"
BTN_BY_FIELD = "🌾 По полю"
BTN_SEASON = "🏆 За сезон"
BTN_NEXT = "🚿 Следующая заправка"
BTN_PARTIAL = "🎯 Заправка на площадь"
BTN_TOTAL = "📊 Текущий итог"
BTN_PLANNED_REFILLS = "🧮 Всего заправок"
BTN_FINISH = "✅ Завершить поле"

BTN_FIELDS = "🌾 Поля"
BTN_CULTURES = "🌱 Культуры"
BTN_CHEM = "🧪 Химия"
BTN_FILLERS = "👤 Заправщики"
BTN_TRACTORS = "🚜 Тракторы"
BTN_TANK_VOLUMES = "🚿 Баки опрыскивателя"
BTN_WATER_RATES = "💧 Расход воды"
BTN_ADMINS = "👑 Администраторы"
BTN_ADD_ADMIN = "➕ Добавить администратора"
BTN_REMOVE_ADMIN = "🗑 Удалить администратора"
BTN_LIST_ADMINS = "📋 Список администраторов"
BTN_CONFIRM_REMOVE_ADMIN = "✅ Да, удалить администратора"

BTN_ADD = "➕ Добавить"
BTN_EDIT = "✏️ Изменить"
BTN_EDIT_CULTURE = "🌱 Изменить культуру"
BTN_DELETE = "🗑 Удалить"
BTN_LIST = "📋 Список"
BTN_BACK = "⬅️ Назад"
BTN_CANCEL = "❌ Отмена"

BTN_ADD_CHEM = "➕ Добавить препарат"
BTN_CHEM_DONE = "✅ Химия выбрана"

DEFAULT_CULTURES = [
    "Пшеница", "Ячмень", "Подсолнечник", "Рапс", "Горох", "Лён", "Нет"
]

# Начальная копия полей из проекта «Обработка полей».
# В дальнейшем список редактируется непосредственно в новом боте.
DEFAULT_FIELDS = [
    ("1", 1.0, "Нет"),
    ("10 возле 23", 10.0, "Нет"),
    ("10 гориз", 10.0, "Нет"),
    ("10 рыбачок", 10.0, "Нет"),
    ("105 -3я бр", 103.0, "Рапс"),
    ("105 возле базы", 105.0, "Пшеница"),
    ("110 огороды", 110.0, "Рапс"),
    ("114 -3я бр", 114.0, "Рапс"),
    ("12 Дебиляк", 12.0, "Нет"),
    ("12 дальнее", 12.0, "Нет"),
    ("123 было 133", 123.0, "Рапс"),
    ("143", 140.0, "Пшеница"),
    ("20 пеньки", 20.0, "Нет"),
    ("23", 23.0, "Рапс"),
    ("25 Рейзер", 25.0, "Нет"),
    ("44 трасса слева", 44.0, "Пшеница"),
    ("45 огороды", 45.0, "Рапс"),
    ("45 трасса справа", 45.0, "Пшеница"),
    ("47 Сады", 47.0, "Рапс"),
    ("47 возле 130", 47.0, "Нет"),
    ("50 Арциз", 50.0, "Нет"),
    ("50 дальнее", 50.0, "Рапс"),
    ("6 поп", 6.0, "Нет"),
    ("62", 62.0, "Рапс"),
    ("78", 78.0, "Пшеница"),
    ("8 поп", 8.0, "Нет"),
    ("91 воинская", 91.0, "Нет"),
]

# Для первого запуска достаточно базовых препаратов из примера.
# Остальные препараты можно добавлять через меню бота.
DEFAULT_CHEMICALS = [
    ('Авангард Зернові (20л)', "л"),
    ('Авангард Ріпак (20л)', "л"),
    ('Авангард бор (20л)', "л"),
    ('Авіатор (5 л)', "л"),
    ('АГЕНТ СЕ (5 л)', "л"),
    ('Агритокс (10л)', "л"),
    ('Агростар,РК (20л)', "л"),
    ('Адексар СЕ Плюс, к.е.', "л"),
    ('Аканто Плюс (5 л)', "л"),
    ('Альтерно (5 л)', "л"),
    ('Антигусень (5 л)', "л"),
    ('Антіколорад,КС (5 л)', "л"),
    ('Асгард (5 л)', "л"),
    ('АЦ ЛЮКС (5 л)', "л"),
    ('Базагран (10 л)', "л"),
    ('Белт 48%, к.с.(1 л)', "л"),
    ('Бродівіт, розчин ( 5 л)', "л"),
    ('Вейрон (1 л)', "л"),
    ('ВЕНОН КС (5 л)', "л"),
    ('Венцедор (1 л)', "л"),
    ('Вето (5 л)', "л"),
    ('Віволт Пар (прилипач) (5 л)', "л"),
    ('Геліантекс 68', "л"),
    ('Генезис (5 л)', "л"),
    ('Гліфовіт, Екстра (20л)', "л"),
    ('Гліфовіт, РК (20л)', "л"),
    ('Голд стар,ВГ (50г)', "л"),
    ('Гродил макси (1 л)', "л"),
    ('Дайфеназол (5 л)', "л"),
    ('Дезерал Екстра, РР (5 л)', "л"),
    ('Дерби (0,5 кг) флакон', "л"),
    ('Десикант ЕЙР (20л)', "л"),
    ('Джин Газация склада', "л"),
    ('Диво Н,РК (5 л)', "л"),
    ('Евро-Лайтнинг (10 л)', "л"),
    ('Екзор (5 л)', "л"),
    ('Етасил', "л"),
    ('Жук off (5 л)', "л"),
    ('Захисник Екстра (5 л)', "л"),
    ('Імі віт (5 л)', "л"),
    ('Імпакт Т (5 л)', "л"),
    ('ІНГРЕС (5 л)', "л"),
    ('Інферно, ВГ (25кг)', "л"),
    ('Капітал (5 л)', "л"),
    ('Карбамід марки Б в біг-бегах', "л"),
    ('КАС 32', "л"),
    ('Квін Стар Макс,КЕ (5 л)', "л"),
    ('Кінто Дуо (10 л)', "л"),
    ('Клабріс КЕ (10 л)', "л"),
    ('Кларк (1кг)', "л"),
    ('Колосаль про (5 л)', "л"),
    ('Лайвіт (5 л)', "л"),
    ('Макстар (5 л)', "л"),
    ('Моноаммоний фосфат', "л"),
    ('Нарапс (5 л)', "л"),
    ('Паллас Екстра', "л"),
    ('Пассат BASF (10 л)', "л"),
    ('Пікадор (20л)', "л"),
    ('Проматріс, КС (5 л)', "л"),
    ('Пульсар флекс 2,5% (10 л)', "л"),
    ('Рекс Дуо (10 л)', "л"),
    ('Ріальт (5 л)', "л"),
    ('Рондос', "л"),
    ('Селфос табл', "л"),
    ('Сінан (5 л)', "л"),
    ('Скайвей XPRO к.е. (5 л)', "л"),
    ('Тандем (20л)', "л"),
    ('Тенеріс 90', "л"),
    ('Ті Рекс (5 л)', "л"),
    ('Тізер, КЕ (20л)', "л"),
    ('ТОП ЕФЕКТ,КС (5 л)', "л"),
    ('Топэфект ( 5 л)', "л"),
    ('Добриво NPK 15:40:10', "л"),
    ('Ультрасил ДУО (5 л)', "л"),
    ('Унікаль (5 л)', "л"),
    ('ФАС (5 л)', "л"),
    ('Флагман (20л)', "л"),
    ('Хізалофоп-Е-Єстіл (5 л)', "л"),
    ('Хлормекват хлорид ( 20л)', "л"),
    ('Хлорпірівіт-агро,КЕ (20л)', "л"),
    ('Хлорпірівіт-агро,КС (20л)', "л"),
]


def local_now():
    return datetime.now(TZ).replace(tzinfo=None)


def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def number(text):
    try:
        return float(str(text).replace(" ", "").replace(",", "."))
    except Exception:
        return None


def fmt(value):
    return f"{float(value or 0):.2f}".replace(".", ",")


def fmt_setting(value):
    return f"{float(value):.2f}".rstrip("0").rstrip(".").replace(".", ",")


def setting_label(table, value):
    unit = "л" if table == "tank_volumes" else "л/га"
    return f"{fmt_setting(value)} {unit}"


def setting_title(table):
    return BTN_TANK_VOLUMES if table == "tank_volumes" else BTN_WATER_RATES


def keyboard(rows):
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def main_kb(uid=None):
    rows = [
        [BTN_NEW, BTN_REPORTS],
        [BTN_PLAN_JOB],
        [BTN_REFILL_HISTORY],
        [BTN_CORRECT_LAST, BTN_DELETE_JOB],
        [BTN_FIELDS, BTN_CULTURES],
        [BTN_CHEM, BTN_FILLERS],
        [BTN_TRACTORS],
        [BTN_TANK_VOLUMES, BTN_WATER_RATES],
    ]
    if uid is not None and is_admin(uid):
        rows.append([BTN_ADMINS])
    return keyboard(rows)


def active_kb(uid=None):
    rows = [
        [BTN_NEXT, BTN_PARTIAL],
        [BTN_TOTAL, BTN_PLANNED_REFILLS],
        [BTN_PLAN_JOB],
        [BTN_REPORTS, BTN_REFILL_HISTORY],
        [BTN_FINISH],
    ]
    if uid is not None and is_admin(uid):
        rows.append([BTN_ADMINS])
    return keyboard(rows)


def admins_kb():
    return keyboard([
        [BTN_ADD_ADMIN], [BTN_REMOVE_ADMIN],
        [BTN_LIST_ADMINS], [BTN_BACK],
    ])


def section_kb(table=None):
    rows = [[BTN_ADD, BTN_EDIT], [BTN_DELETE, BTN_LIST]]
    if table == "fields":
        rows.append([BTN_EDIT_CULTURE])
    rows.append([BTN_BACK])
    return keyboard(rows)


def reports_kb():
    return keyboard([
        [BTN_TODAY, BTN_BY_DATE],
        [BTN_BY_FIELD, BTN_SEASON],
        [BTN_BACK],
    ])


def date_label(iso_text):
    try:
        return datetime.fromisoformat(iso_text).strftime("%d.%m.%Y")
    except Exception:
        return str(iso_text)[:10]


def rows_kb(items, back=True):
    rows = [[x] for x in items]
    if back:
        rows.append([BTN_BACK])
    return keyboard(rows)


async def choose_setting(update, state, table, mode):
    uid = update.effective_user.id
    with db() as c:
        rows = c.execute(
            f"SELECT value FROM {table} WHERE active=1 ORDER BY value"
        ).fetchall()
    if not rows:
        flow.pop(uid, None)
        await update.message.reply_text(
            f"Список пуст. Сначала добавьте значение в разделе «{setting_title(table)}».",
            reply_markup=active_kb(uid) if active_job(uid) else main_kb(uid)
        )
        return
    state["mode"] = mode
    state["values"] = {setting_label(table, r["value"]): r["value"] for r in rows}
    flow[uid] = state
    await update.message.reply_text(
        "Выберите объём бака опрыскивателя:" if table == "tank_volumes"
        else "Выберите норму расхода воды:",
        reply_markup=rows_kb(state["values"].keys())
    )


async def handle_numeric_section(update, state, text):
    uid = update.effective_user.id
    table = state["table"]
    title = setting_title(table)
    mode = state["mode"]
    if mode == "numeric_section":
        if text == BTN_LIST:
            with db() as c:
                rows = c.execute(
                    f"SELECT value FROM {table} WHERE active=1 ORDER BY value"
                ).fetchall()
            lines = [f"• {setting_label(table, r['value'])}" for r in rows]
            await update.message.reply_text(
                f"📋 {title}\n\n" + ("\n".join(lines) if lines else "Список пуст."),
                reply_markup=section_kb(table)
            )
            return
        if text == BTN_ADD:
            state["mode"] = "numeric_add"
            await update.message.reply_text(
                "Введите объём бака в литрах, например 3000 или 3200:"
                if table == "tank_volumes" else
                "Введите расход воды в л/га, например 100 или 110:"
            )
            return
        if text in (BTN_EDIT, BTN_DELETE):
            with db() as c:
                rows = c.execute(
                    f"SELECT id,value FROM {table} WHERE active=1 ORDER BY value"
                ).fetchall()
            if not rows:
                await update.message.reply_text("Список пуст. Сначала добавьте значение.")
                return
            mapping = {setting_label(table, r["value"]): r["id"] for r in rows}
            flow[uid] = {
                "mode": "numeric_select", "table": table,
                "action": "edit" if text == BTN_EDIT else "delete", "map": mapping,
            }
            await update.message.reply_text(
                "Что изменить?" if text == BTN_EDIT else "Что удалить?",
                reply_markup=rows_kb(mapping.keys())
            )
            return
    if mode == "numeric_select":
        if text not in state["map"]:
            await update.message.reply_text("Выберите значение кнопкой.")
            return
        item_id = state["map"][text]
        if state["action"] == "delete":
            with db() as c:
                c.execute(f"UPDATE {table} SET active=0 WHERE id=?", (item_id,))
            flow[uid] = {"mode": "numeric_section", "table": table}
            await update.message.reply_text(
                "🗑 Удалено из списка. Старые работы сохранены.",
                reply_markup=section_kb(table)
            )
            return
        flow[uid] = {"mode": "numeric_edit", "table": table, "id": item_id}
        await update.message.reply_text(f"Текущее значение: {text}\nВведите новое число:")
        return
    if mode in ("numeric_add", "numeric_edit"):
        value = number(text)
        upper_limit = 1000000 if table == "tank_volumes" else 10000
        if value is None or not math.isfinite(value) or not 0 < value <= upper_limit:
            await update.message.reply_text("Введите положительное число, например 3000 или 110.")
            return
        with db() as c:
            if mode == "numeric_add":
                c.execute(f"INSERT OR IGNORE INTO {table}(value) VALUES(?)", (value,))
                c.execute(f"UPDATE {table} SET active=1 WHERE value=?", (value,))
            else:
                try:
                    c.execute(f"UPDATE {table} SET value=? WHERE id=?", (value, state["id"]))
                except sqlite3.IntegrityError:
                    await update.message.reply_text("Такое значение уже есть. Введите другое.")
                    return
        flow[uid] = {"mode": "numeric_section", "table": table}
        await update.message.reply_text(
            f"✅ Сохранено: {setting_label(table, value)}."
            " Старые работы не изменены.",
            reply_markup=section_kb(table)
        )


def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS fields(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            area REAL NOT NULL,
            culture TEXT,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS cultures(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS chemicals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            unit TEXT NOT NULL DEFAULT 'л',
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS fillers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS tractors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            water_capacity_l REAL NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS tank_volumes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL NOT NULL UNIQUE,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS water_rates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value REAL NOT NULL UNIQUE,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS bot_admins(
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS bot_users(
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            field_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            field_area REAL NOT NULL,
            culture TEXT NOT NULL,
            tank_volume REAL NOT NULL,
            water_rate REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            started_at TEXT NOT NULL,
            finished_at TEXT
        );

        CREATE TABLE IF NOT EXISTS recipes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            chemical_id INTEGER,
            chemical_name TEXT NOT NULL,
            unit TEXT NOT NULL,
            rate_per_ha REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS refills(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            seq INTEGER NOT NULL,
            refill_type TEXT NOT NULL,
            target_ha REAL NOT NULL,
            residual_l REAL NOT NULL,
            total_solution_l REAL NOT NULL,
            water_to_add_l REAL NOT NULL,
            filler_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            end_residual_l REAL,
            actual_sprayed_ha REAL,
            closed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS refill_chemicals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            refill_id INTEGER NOT NULL,
            chemical_name TEXT NOT NULL,
            unit TEXT NOT NULL,
            rate_per_ha REAL NOT NULL,
            amount REAL NOT NULL
        );
        """)

        # Миграция старой базы: новые поля для фактической выработки.
        job_cols = {r["name"] for r in c.execute("PRAGMA table_info(jobs)").fetchall()}
        for col, ddl in [
            ("tractor_id", "INTEGER"),
            ("tractor_name", "TEXT"),
            ("water_capacity_l", "REAL"),
            ("entered_by_id", "INTEGER"),
            ("entered_by_name", "TEXT"),
            ("entered_by_role", "TEXT"),
        ]:
            if col not in job_cols:
                c.execute(f"ALTER TABLE jobs ADD COLUMN {col} {ddl}")
        refill_cols = {r["name"] for r in c.execute("PRAGMA table_info(refills)").fetchall()}
        for col, ddl in [
            ("end_residual_l", "REAL"),
            ("actual_sprayed_ha", "REAL"),
            ("closed_at", "TEXT"),
            ("entered_by_id", "INTEGER"),
            ("entered_by_name", "TEXT"),
            ("entered_by_role", "TEXT"),
            ("closed_by_id", "INTEGER"),
            ("closed_by_name", "TEXT"),
            ("closed_by_role", "TEXT"),
        ]:
            if col not in refill_cols:
                c.execute(f"ALTER TABLE refills ADD COLUMN {col} {ddl}")

        # Переносим ранее введённые значения из работ в новые справочники.
        # Данные самих работ и их отчёты при этом не меняются.
        c.execute(
            """INSERT OR IGNORE INTO tank_volumes(value)
               SELECT DISTINCT tank_volume FROM jobs WHERE tank_volume>0"""
        )
        c.execute(
            """INSERT OR IGNORE INTO water_rates(value)
               SELECT DISTINCT water_rate FROM jobs WHERE water_rate>0"""
        )

        if c.execute("SELECT COUNT(*) n FROM fields").fetchone()["n"] == 0:
            c.executemany(
                "INSERT INTO fields(name,area,culture) VALUES(?,?,?)",
                DEFAULT_FIELDS
            )

        if c.execute("SELECT COUNT(*) n FROM cultures").fetchone()["n"] == 0:
            c.executemany(
                "INSERT INTO cultures(name) VALUES(?)",
                [(x,) for x in DEFAULT_CULTURES]
            )

        # Полный список химии из «Обработки полей».
        # Добавляем недостающие позиции в уже существующую постоянную базу,
        # не удаляя пользовательские препараты.
        for chem_name, chem_unit in DEFAULT_CHEMICALS:
            c.execute(
                """INSERT INTO chemicals(name,unit,active) VALUES(?,?,1)
                   ON CONFLICT(name) DO UPDATE SET unit=excluded.unit,active=1""",
                (chem_name, chem_unit)
            )

        # Тестовые АБ 1–АБ 5 больше не показываем.
        for test_name in ("АБ 1", "АБ 2", "АБ 3", "АБ 4", "АБ 5"):
            c.execute("UPDATE chemicals SET active=0 WHERE name=?", (test_name,))


def active_job(uid):
    with db() as c:
        return c.execute(
            "SELECT * FROM jobs WHERE user_id=? AND status='active' "
            "ORDER BY id DESC LIMIT 1",
            (uid,)
        ).fetchone()


def is_admin(uid):
    if ADMIN_ID and uid == ADMIN_ID:
        return True
    with db() as c:
        return c.execute(
            "SELECT 1 FROM bot_admins WHERE user_id=?", (uid,)
        ).fetchone() is not None


def display_name(update):
    user = update.effective_user
    return (" ".join(filter(None, [user.first_name, user.last_name])).strip()
            or user.username or str(user.id))


def remember_user(update):
    with db() as c:
        c.execute(
            """INSERT INTO bot_users(user_id,name) VALUES(?,?)
               ON CONFLICT(user_id) DO UPDATE SET name=excluded.name""",
            (update.effective_user.id, display_name(update))
        )


def entry_actor(update):
    uid = update.effective_user.id
    return uid, display_name(update), "администратор" if is_admin(uid) else "пользователь"


def actor_label(actor_id, saved_name, saved_role, known_users):
    if actor_id is None:
        return "не зафиксировано"
    name = saved_name or known_users.get(actor_id) or f"ID {actor_id}"
    role = saved_role or ("администратор" if actor_id == ADMIN_ID else "")
    return f"{role} {name}" if role else name


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    remember_user(update)
    await update.message.reply_text(f"Ваш Telegram ID: {update.effective_user.id}")


def planned_refills(job):
    """Полный план по полю: заправки бака и подвоз воды считаются отдельно."""
    total_water = float(job["field_area"]) * float(job["water_rate"])
    tank = float(job["tank_volume"])
    fills = total_water / tank
    full_fills = math.ceil(fills - 1e-10)
    last_tank = total_water - tank * (full_fills - 1)
    lines = [
        "🧮 ПЛАН ЗАПРАВОК НА ВСЁ ПОЛЕ", "",
        f"🌾 {job['field_name']} | {job['culture']}",
        f"🎯 Площадь: {fmt(job['field_area'])} га",
        f"💧 Норма воды: {fmt(job['water_rate'])} л/га",
        f"💧 Всего раствора: {fmt(total_water)} л",
        f"🚿 Бак опрыскивателя: {fmt(tank)} л",
        f"🚿 Заправок опрыскивателя: {fills:.1f}".replace(".", ","),
        f"Последняя заправка: {fmt(last_tank)} л",
    ]
    capacity = job["water_capacity_l"]
    if capacity and capacity > 0:
        loads = total_water / capacity
        full_loads = math.ceil(loads - 1e-10)
        last_load = total_water - capacity * (full_loads - 1)
        lines += [
            "", f"🚜 {job['tractor_name']} | Вода в прицепе: {fmt(capacity)} л",
            f"🛢 Подвозов воды: {loads:.1f}".replace(".", ","),
            f"Последний подвоз: {fmt(last_load)} л",
        ]
        full_tanks = int(capacity // tank)
        if full_tanks:
            tank_word = ("полная заправка" if full_tanks % 10 == 1 and full_tanks % 100 != 11
                         else "полные заправки" if full_tanks % 10 in (2, 3, 4)
                         and full_tanks % 100 not in (12, 13, 14) else "полных заправок")
            lines.append(
                f"Из полного прицепа: {full_tanks} {tank_word} бака, "
                f"остаток {fmt(capacity - full_tanks * tank)} л"
            )
    return lines


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if flow.get(uid, {}).get("mode", "").startswith("plan_"):
        flow.pop(uid, None)
    remember_user(update)
    if is_admin(uid) and uid != ADMIN_ID:
        name = " ".join(filter(None, [update.effective_user.first_name,
                                       update.effective_user.last_name]))
        with db() as c:
            c.execute("UPDATE bot_admins SET name=? WHERE user_id=?", (name, uid))
    job = active_job(update.effective_user.id)
    await update.message.reply_text(
        "🚿 ОПРЫСКИВАНИЕ\n\n"
        + ("Есть активная работа." if job else "Готов к работе."),
        reply_markup=active_kb(uid) if job else main_kb(uid)
    )


async def begin_job(update):
    uid = update.effective_user.id
    with db() as c:
        rs = c.execute(
            "SELECT id,name,water_capacity_l FROM tractors WHERE active=1 ORDER BY name"
        ).fetchall()

    if not rs:
        await update.message.reply_text(
            "Сначала добавьте трактор и объём его бочки в разделе «🚜 Тракторы».",
            reply_markup=main_kb(uid)
        )
        return

    mapping = {f"🚜 {r['name']} | {fmt(r['water_capacity_l'])} л": r["id"] for r in rs}
    flow[uid] = {"mode": "job_tractor", "map": mapping}
    await update.message.reply_text("🚜 Выберите трактор:", reply_markup=rows_kb(mapping.keys()))


async def begin_plan_job(update):
    uid = update.effective_user.id
    with db() as c:
        tractors = c.execute(
            "SELECT id,name,water_capacity_l FROM tractors WHERE active=1 ORDER BY name"
        ).fetchall()
    if not tractors:
        await update.message.reply_text(
            "Сначала добавьте трактор и объём прицепа с водой в разделе «🚜 Тракторы».",
            reply_markup=active_kb(uid) if active_job(uid) else main_kb(uid)
        )
        return
    mapping = {
        f"🚜 {r['name']} | {fmt(r['water_capacity_l'])} л": dict(r)
        for r in tractors
    }
    flow[uid] = {"mode": "plan_tractor", "map": mapping}
    await update.message.reply_text(
        "📋 ЗАПЛАНИРОВАННОЕ ЗАДАНИЕ\nВыберите трактор с прицепом воды:",
        reply_markup=rows_kb(mapping.keys())
    )


async def choose_plan_field(update, tractor):
    uid = update.effective_user.id
    with db() as c:
        fields = c.execute(
            "SELECT id,name,area,culture FROM fields WHERE active=1 ORDER BY name"
        ).fetchall()
    mapping = {f"🌾 {r['name']} | {fmt(r['area'])} га": dict(r) for r in fields}
    flow[uid] = {"mode": "plan_field", "tractor": tractor, "map": mapping}
    await update.message.reply_text("🌾 Выберите поле:", reply_markup=rows_kb(mapping.keys()))


async def choose_plan_chemical(update, state):
    uid = update.effective_user.id
    with db() as c:
        chemicals = c.execute(
            "SELECT name,unit FROM chemicals WHERE active=1 ORDER BY name"
        ).fetchall()
    mapping = {f"🧪 {r['name']}": dict(r) for r in chemicals}
    state["mode"] = "plan_chemical"
    state["map"] = mapping
    flow[uid] = state
    await update.message.reply_text(
        "🧪 Выберите препарат для расчёта:",
        reply_markup=rows_kb([*mapping.keys(), BTN_CHEM_DONE])
    )


async def finish_plan_job(update, state):
    uid = update.effective_user.id
    field = state["field"]
    tractor = state["tractor"]
    water_rate = state["water_rate"]
    tank = state["tank"]
    first_solution = min(tank, float(field["area"]) * water_rate)
    first_area = first_solution / water_rate
    plan = {
        "field_name": field["name"], "field_area": field["area"],
        "culture": state["culture"], "tank_volume": tank,
        "water_rate": water_rate, "tractor_name": tractor["name"],
        "water_capacity_l": tractor["water_capacity_l"],
    }
    lines = ["📋 ЗАПЛАНИРОВАННОЕ ЗАДАНИЕ", ""] + planned_refills(plan)
    lines += [
        "", "🚿 ПЕРВАЯ ЗАПРАВКА (ПУСТОЙ БАК)",
        f"💧 Приготовить раствора: {fmt(first_solution)} л",
        f"🎯 Хватит на: {fmt(first_area)} га",
    ]
    if state["recipe"]:
        lines += ["🧪 Добавить в первую заправку:"]
        for chem in state["recipe"]:
            lines.append(
                f"• {chem['name']} — {fmt(first_area * chem['rate'])} {chem['unit']}"
            )
        lines += ["", "🧪 ХИМИЯ НА ВСЁ ПОЛЕ:"]
        for chem in state["recipe"]:
            lines.append(
                f"• {chem['name']}: {fmt(chem['rate'])} {chem['unit']}/га"
                f" → {fmt(float(field['area']) * chem['rate'])} {chem['unit']}"
            )
    lines += ["", "ℹ️ Расчёт справочный, в отчёты не записан."]
    flow.pop(uid, None)
    page = []
    for line in lines:
        if page and len("\n".join(page)) + len(line) + 1 > 3800:
            await update.message.reply_text("\n".join(page))
            page = ["📋 ЗАПЛАНИРОВАННОЕ ЗАДАНИЕ (продолжение)", ""]
        page.append(line)
    await update.message.reply_text(
        "\n".join(page), reply_markup=active_kb(uid) if active_job(uid) else main_kb(uid)
    )


async def handle_plan_job(update, state, text):
    mode = state["mode"]
    if mode == "plan_tractor":
        if text in state["map"]:
            await choose_plan_field(update, state["map"][text])
        else:
            await update.message.reply_text("Выберите трактор кнопкой.")
        return
    if mode == "plan_field":
        if text not in state["map"]:
            await update.message.reply_text("Выберите поле кнопкой.")
            return
        state["field"] = state["map"][text]
        with db() as c:
            cultures = [r["name"] for r in c.execute(
                "SELECT name FROM cultures WHERE active=1 ORDER BY name"
            ).fetchall()]
        state["mode"] = "plan_culture"
        state["cultures"] = cultures
        await update.message.reply_text(
            f"🌱 Выберите культуру (сейчас у поля: {state['field']['culture']}):",
            reply_markup=rows_kb(cultures)
        )
        return
    if mode == "plan_culture":
        if text not in state["cultures"]:
            await update.message.reply_text("Выберите культуру кнопкой.")
            return
        state["culture"] = text
        await choose_setting(update, state, "tank_volumes", "plan_tank")
        return
    if mode == "plan_tank":
        if text not in state["values"]:
            await update.message.reply_text("Выберите бак из списка кнопкой.")
            return
        state["tank"] = state["values"][text]
        await choose_setting(update, state, "water_rates", "plan_water_rate")
        return
    if mode == "plan_water_rate":
        if text not in state["values"]:
            await update.message.reply_text("Выберите расход воды из списка кнопкой.")
            return
        state["water_rate"] = state["values"][text]
        state["recipe"] = []
        await choose_plan_chemical(update, state)
        return
    if mode == "plan_chemical":
        if text == BTN_CHEM_DONE:
            await finish_plan_job(update, state)
            return
        if text not in state["map"]:
            await update.message.reply_text("Выберите препарат кнопкой.")
            return
        state["chemical"] = state["map"][text]
        state["mode"] = "plan_chem_rate"
        chem = state["chemical"]
        await update.message.reply_text(
            f"🧪 {chem['name']}\nВведите норму на 1 га ({chem['unit']}/га):"
        )
        return
    if mode == "plan_chem_rate":
        rate = number(text)
        if rate is None or not math.isfinite(rate) or rate < 0:
            await update.message.reply_text("Введите норму числом, например 0,15.")
            return
        chem = state["chemical"]
        state["recipe"].append({"name": chem["name"], "unit": chem["unit"], "rate": rate})
        state["mode"] = "plan_more"
        await update.message.reply_text(
            "✅ Препарат добавлен в расчёт.",
            reply_markup=keyboard([[BTN_ADD_CHEM, BTN_CHEM_DONE], [BTN_CANCEL]])
        )
        return
    if mode == "plan_more":
        if text == BTN_ADD_CHEM:
            await choose_plan_chemical(update, state)
        elif text == BTN_CHEM_DONE:
            await finish_plan_job(update, state)
        else:
            await update.message.reply_text("Выберите «Добавить препарат» или «Химия выбрана».")


async def choose_job_field(update, tractor):
    uid = update.effective_user.id
    with db() as c:
        rs = c.execute(
            "SELECT id,name,area FROM fields WHERE active=1 ORDER BY name"
        ).fetchall()

    mapping = {f"🌾 {r['name']} | {fmt(r['area'])} га": r["id"] for r in rs}
    flow[uid] = {"mode": "field", "map": mapping, "tractor": tractor}

    await update.message.reply_text(
        "🌾 Выберите поле:",
        reply_markup=rows_kb(mapping.keys())
    )


async def choose_chemical(update, job_id):
    uid = update.effective_user.id
    with db() as c:
        rs = c.execute(
            "SELECT id,name,unit FROM chemicals WHERE active=1 ORDER BY name"
        ).fetchall()

    mapping = {f"🧪 {r['name']}": r["id"] for r in rs}
    flow[uid] = {"mode": "chem", "job_id": job_id, "map": mapping}

    await update.message.reply_text(
        "🧪 Выберите препарат:",
        reply_markup=rows_kb(mapping.keys())
    )


def close_previous_refill(job, residual, update):
    """Закрывает предыдущую незакрытую заправку по остатку перед новой."""
    with db() as c:
        prev = c.execute(
            """SELECT * FROM refills
               WHERE job_id=? AND end_residual_l IS NULL
               ORDER BY seq DESC LIMIT 1""",
            (job["id"],)
        ).fetchone()

        if not prev:
            return None

        if residual > prev["total_solution_l"] + 0.0001:
            return {"error": (
                f"Остаток {fmt(residual)} л больше объёма предыдущей "
                f"заправки {fmt(prev['total_solution_l'])} л."
            )}

        used_l = max(0.0, prev["total_solution_l"] - residual)
        actual_ha = used_l / job["water_rate"]
        actor_id, actor_name, actor_role = entry_actor(update)

        c.execute(
            """UPDATE refills
               SET end_residual_l=?, actual_sprayed_ha=?, closed_at=?,
                   closed_by_id=?,closed_by_name=?,closed_by_role=?
               WHERE id=?""",
            (
                residual, actual_ha,
                local_now().isoformat(timespec="seconds"),
                actor_id, actor_name, actor_role,
                prev["id"]
            )
        )

        # Фактически израсходованная химия предыдущей заправки:
        # доля использованного раствора × количество химии, находившееся
        # в приготовленном объёме этой заправки.
        # refill_chemicals хранит добавленную химию. Для рабочего раствора
        # фактический расход корректно считаем по норме × фактические гектары.
        return {
            "seq": prev["seq"],
            "actual_ha": actual_ha,
            "used_l": used_l,
            "residual": residual,
        }


async def choose_filler(update, refill_type, target_ha, residual):
    uid = update.effective_user.id
    with db() as c:
        rs = c.execute(
            "SELECT name FROM fillers WHERE active=1 ORDER BY name"
        ).fetchall()

    if not rs:
        flow.pop(uid, None)
        await update.message.reply_text(
            "⚠️ Сначала добавьте хотя бы одного заправщика.",
            reply_markup=active_kb(uid)
        )
        return

    names = [r["name"] for r in rs]
    flow[uid] = {
        "mode": "filler",
        "refill_type": refill_type,
        "target_ha": target_ha,
        "residual": residual,
        "fillers": names,
    }

    await update.message.reply_text(
        "👤 Выберите заправщика:",
        reply_markup=rows_kb(names)
    )


async def save_refill(update, job, refill_type, target_ha, residual, filler):
    # В режиме «полная» химия добавляется только на объём,
    # которого не хватает до полного бака.
    if refill_type == "full":
        water_to_add = max(0.0, job["tank_volume"] - residual)
        target_ha = water_to_add / job["water_rate"]
        total_solution = job["tank_volume"]
    else:
        # Специальная заправка на остаток площади:
        # 7 га × 110 = 770 л общего раствора;
        # если в баке 200 л, долить воды = 570 л.
        total_solution = target_ha * job["water_rate"]
        water_to_add = max(0.0, total_solution - residual)

    with db() as c:
        actor_id, actor_name, actor_role = entry_actor(update)
        seq = c.execute(
            "SELECT COALESCE(MAX(seq),0)+1 n FROM refills WHERE job_id=?",
            (job["id"],)
        ).fetchone()["n"]

        cur = c.execute(
            """INSERT INTO refills(
                job_id,seq,refill_type,target_ha,residual_l,
                total_solution_l,water_to_add_l,filler_name,created_at,
                entered_by_id,entered_by_name,entered_by_role
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                job["id"], seq, refill_type, target_ha, residual,
                total_solution, water_to_add, filler,
                local_now().isoformat(timespec="seconds"),
                actor_id, actor_name, actor_role
            )
        )
        refill_id = cur.lastrowid

        recipe = c.execute(
            "SELECT * FROM recipes WHERE job_id=? ORDER BY id",
            (job["id"],)
        ).fetchall()

        chemical_ha = water_to_add / job["water_rate"]
        for r in recipe:
            # В остатке уже есть рабочий раствор с химией.
            # Поэтому новую химию добавляем только на доливаемую воду.
            amount = chemical_ha * r["rate_per_ha"]
            c.execute(
                """INSERT INTO refill_chemicals(
                    refill_id,chemical_name,unit,rate_per_ha,amount
                ) VALUES(?,?,?,?,?)""",
                (
                    refill_id, r["chemical_name"], r["unit"],
                    r["rate_per_ha"], amount
                )
            )

    lines = [
        f"🚿 ЗАПРАВКА №{seq}",
        "",
        f"🌾 Поле: {job['field_name']}",
        f"🌱 Культура: {job['culture']}",
        f"👤 Заправщик: {filler}",
        f"🕐 Время заправки: {local_now().strftime('%H:%M')}",
        "",
        f"🎯 Площадь: {fmt(target_ha)} га",
        f"💧 Норма воды: {fmt(job['water_rate'])} л/га",
        f"💧 Нужно раствора: {fmt(total_solution)} л",
        f"💧 Остаток в баке: {fmt(residual)} л",
        f"➕ Долить воды: {fmt(water_to_add)} л",
        "",
        f"🧮 Химия рассчитывается на: {fmt(water_to_add / job['water_rate'])} га",
        "",
        "🧪 ДОБАВИТЬ:"
    ]

    chemical_ha = water_to_add / job["water_rate"]
    for r in recipe:
        lines.append(
            f"• {r['chemical_name']} — "
            f"{fmt(chemical_ha * r['rate_per_ha'])} {r['unit']}"
        )

    if seq == 1:
        lines += [""] + planned_refills(job) + ["", "🧪 ХИМИЯ НА ВСЁ ПОЛЕ:"]
        for r in recipe:
            lines.append(
                f"• {r['chemical_name']}: {fmt(r['rate_per_ha'])} {r['unit']}/га"
                f" → {fmt(float(job['field_area']) * r['rate_per_ha'])} {r['unit']}"
            )

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=active_kb(update.effective_user.id)
    )


async def show_total(update, job):
    with db() as c:
        refills = c.execute(
            "SELECT * FROM refills WHERE job_id=? ORDER BY seq",
            (job["id"],)
        ).fetchall()

        chems = c.execute(
            """SELECT rc.chemical_name,rc.unit,SUM(rc.amount) amount
               FROM refill_chemicals rc
               JOIN refills r ON r.id=rc.refill_id
               WHERE r.job_id=?
               GROUP BY rc.chemical_name,rc.unit
               ORDER BY rc.chemical_name""",
            (job["id"],)
        ).fetchall()

    prepared_ha = sum(x["target_ha"] for x in refills)
    actual_ha = sum(float(x["actual_sprayed_ha"] or 0) for x in refills)
    water = sum(x["water_to_add_l"] for x in refills)

    lines = [
        "📊 ТЕКУЩИЙ ИТОГ",
        "",
        f"🌾 {job['field_name']} | {job['culture']}",
        f"🚿 Заправок: {len(refills)}",
        f"🚜 Фактически обработано: {fmt(actual_ha)} га",
        f"🎯 Приготовлено на: {fmt(prepared_ha)} га",
        f"💧 Долито воды: {fmt(water)} л",
    ]

    if chems:
        lines += ["", "🧪 Химия:"]
        for r in chems:
            lines.append(
                f"• {r['chemical_name']} — {fmt(r['amount'])} {r['unit']}"
            )

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=active_kb(update.effective_user.id)
    )


def recalc_job_actuals(job_id):
    """Пересчитать фактическую выработку всех закрытых заправок по цепочке остатков."""
    with db() as c:
        job = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        fills = c.execute(
            "SELECT * FROM refills WHERE job_id=? ORDER BY seq,id",
            (job_id,)
        ).fetchall()
        for f in fills:
            if f["end_residual_l"] is None:
                continue
            actual = max(0.0, (float(f["total_solution_l"]) - float(f["end_residual_l"])) / float(job["water_rate"]))
            c.execute(
                "UPDATE refills SET actual_sprayed_ha=? WHERE id=?",
                (actual, f["id"])
            )


def job_summary(job_id):
    with db() as c:
        job = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        total = c.execute(
            "SELECT COALESCE(SUM(actual_sprayed_ha),0) s FROM refills WHERE job_id=?",
            (job_id,)
        ).fetchone()["s"]
        recipe = c.execute(
            "SELECT chemical_name,unit,rate_per_ha FROM recipes WHERE job_id=? ORDER BY id",
            (job_id,)
        ).fetchall()
    return job, float(total or 0), recipe


async def send_report(update, where_sql="", params=(), title="📊 ИТОГ"):
    with db() as c:
        jobs = c.execute(
            f"""SELECT j.*,
                       COALESCE(SUM(r.actual_sprayed_ha),0) actual_ha,
                       COUNT(r.id) refill_count
                FROM jobs j
                LEFT JOIN refills r ON r.job_id=j.id
                WHERE 1=1 {where_sql}
                GROUP BY j.id
                ORDER BY j.started_at, j.id""",
            params
        ).fetchall()

        # Рецепт сохраняется вместе с работой: последующие изменения списка
        # препаратов не должны менять историю обработки по датам.
        recipes = {}
        refill_authors = {}
        known_users = {
            r["user_id"]: r["name"] for r in c.execute(
                "SELECT user_id,name FROM bot_users"
            ).fetchall()
        }
        for j in jobs:
            recipes[j["id"]] = c.execute(
                """SELECT chemical_name,unit,rate_per_ha
                   FROM recipes WHERE job_id=? ORDER BY id""",
                (j["id"],)
            ).fetchall()
            refill_authors[j["id"]] = c.execute(
                """SELECT entered_by_id,entered_by_name,entered_by_role,
                          closed_by_id,closed_by_name,closed_by_role
                   FROM refills WHERE job_id=? ORDER BY seq,id""",
                (j["id"],)
            ).fetchall()

    if not jobs:
        await update.message.reply_text("Записей нет.", reply_markup=reports_kb())
        return

    lines = [title, ""]
    total = 0.0
    for j in jobs:
        ha = float(j["actual_ha"] or 0)
        total += ha
        lines += [
            f"📅 {date_label(j['started_at'])}",
            f"🌾 {j['field_name']} | {j['culture']}",
            f"🚜 Обработано: {fmt(ha)} га",
            f"🚿 Заправок: {j['refill_count']}",
        ]
        if recipes[j["id"]]:
            lines.append("🧪 Химия на обработанную площадь:")
            for r in recipes[j["id"]]:
                lines.append(
                    f"• {r['chemical_name']} — "
                    f"{fmt(ha * r['rate_per_ha'])} {r['unit']} "
                    f"({fmt(r['rate_per_ha'])} {r['unit']}/га)"
                )
        creator = actor_label(
            j["entered_by_id"] or j["user_id"], j["entered_by_name"],
            j["entered_by_role"], known_users
        )
        authors = []
        for r in refill_authors[j["id"]]:
            for prefix in ("entered", "closed"):
                author_id = r[f"{prefix}_by_id"]
                if author_id is not None:
                    author = actor_label(
                        author_id, r[f"{prefix}_by_name"],
                        r[f"{prefix}_by_role"], known_users
                    )
                    if author not in authors:
                        authors.append(author)
        if authors:
            if creator not in authors:
                lines.append(f"👤 Задание создал: {creator}")
            lines.append(
                f"👤 Данные {'ввёл' if len(authors) == 1 else 'ввели'}: "
                + ", ".join(authors)
            )
            if any(r["entered_by_id"] is None for r in refill_authors[j["id"]]):
                lines.append("👤 Кто ввёл часть старых заправок: не зафиксировано")
        else:
            lines.append(f"👤 Задание создал: {creator}")
            if j["refill_count"]:
                lines.append("👤 Кто ввёл старые заправки: не зафиксировано")
        lines.append("")
    lines.append(f"📊 ВСЕГО: {fmt(total)} га")
    # Telegram ограничивает сообщение 4096 символами. Длинные отчёты
    # отправляем несколькими сообщениями в том же порядке.
    page = []
    for line in lines:
        if page and len("\n".join(page)) + len(line) + 1 > 3800:
            await update.message.reply_text("\n".join(page), reply_markup=reports_kb())
            page = [f"{title} (продолжение)", ""]
        page.append(line)
    if page:
        await update.message.reply_text("\n".join(page), reply_markup=reports_kb())


async def choose_report_date(update):
    uid = update.effective_user.id
    with db() as c:
        rs = c.execute(
            """SELECT DISTINCT substr(started_at,1,10) d
               FROM jobs ORDER BY d DESC LIMIT 60"""
        ).fetchall()
    mapping = {}
    for r in rs:
        try:
            label = datetime.fromisoformat(r["d"]).strftime("%d.%m.%Y")
        except Exception:
            label = r["d"]
        mapping[label] = r["d"]
    flow[uid] = {"mode": "report_date", "map": mapping}
    await update.message.reply_text(
        "📅 Выберите дату, по которой уже есть работа:",
        reply_markup=rows_kb(mapping.keys())
    )


async def choose_report_field(update):
    uid = update.effective_user.id
    with db() as c:
        rs = c.execute(
            "SELECT DISTINCT field_name FROM jobs ORDER BY field_name"
        ).fetchall()
    names = [r["field_name"] for r in rs]
    flow[uid] = {"mode": "report_field", "fields": names}
    await update.message.reply_text(
        "🌾 Выберите поле:",
        reply_markup=rows_kb(names)
    )


async def choose_refill_history_field(update):
    uid = update.effective_user.id
    with db() as c:
        rows = c.execute(
            """SELECT DISTINCT j.field_name
               FROM refills r JOIN jobs j ON j.id=r.job_id
               ORDER BY j.field_name"""
        ).fetchall()
    names = [r["field_name"] for r in rows]
    if not names:
        await update.message.reply_text(
            "Сохранённых заправок пока нет.",
            reply_markup=active_kb(uid) if active_job(uid) else main_kb(uid)
        )
        return
    flow[uid] = {"mode": "history_field", "fields": names}
    await update.message.reply_text(
        "📚 История заправок\nВыберите поле:",
        reply_markup=rows_kb(names)
    )


async def choose_refill_history_date(update, field_name):
    uid = update.effective_user.id
    with db() as c:
        rows = c.execute(
            """SELECT DISTINCT substr(r.created_at,1,10) day
               FROM refills r JOIN jobs j ON j.id=r.job_id
               WHERE j.field_name=? ORDER BY day DESC""",
            (field_name,)
        ).fetchall()
    mapping = {date_label(r["day"]): r["day"] for r in rows}
    if not mapping:
        await choose_refill_history_field(update)
        return
    flow[uid] = {"mode": "history_date", "field": field_name, "dates": mapping}
    await update.message.reply_text(
        f"🌾 {field_name}\nВыберите дату заправок:",
        reply_markup=rows_kb(mapping.keys())
    )


async def show_refill_history(update, field_name, day, dates):
    with db() as c:
        rows = c.execute(
            """SELECT r.*,j.field_name,j.culture,j.water_rate
               FROM refills r JOIN jobs j ON j.id=r.job_id
               WHERE j.field_name=? AND substr(r.created_at,1,10)=?
               ORDER BY r.created_at,r.id""",
            (field_name, day)
        ).fetchall()
        known_users = {
            row["user_id"]: row["name"] for row in c.execute(
                "SELECT user_id,name FROM bot_users"
            ).fetchall()
        }
        chemicals = {}
        for r in rows:
            chemicals[r["id"]] = c.execute(
                """SELECT chemical_name,unit,amount FROM refill_chemicals
                   WHERE refill_id=? ORDER BY id""",
                (r["id"],)
            ).fetchall()

    lines = [f"📚 ЗАПРАВКИ: {field_name}", f"📅 {date_label(day)}", ""]
    total_water = 0.0
    total_ha = 0.0
    for r in rows:
        total_water += float(r["water_to_add_l"])
        total_ha += float(r["actual_sprayed_ha"] or 0)
        try:
            time = datetime.fromisoformat(r["created_at"]).strftime("%H:%M")
        except (ValueError, TypeError):
            time = "—"
        lines += [
            f"🚿 ЗАПРАВКА №{r['seq']} | {time}",
            f"🌱 Культура: {r['culture']}",
            f"👤 Заправщик: {r['filler_name']}",
            f"🎯 Приготовлено на: {fmt(r['target_ha'])} га",
            (f"🚜 Обработано: {fmt(r['actual_sprayed_ha'])} га"
             if r["actual_sprayed_ha"] is not None else "🚜 Обработка ещё не завершена"),
            f"💧 Раствора в баке: {fmt(r['total_solution_l'])} л",
            f"💧 Остаток перед заправкой: {fmt(r['residual_l'])} л",
            f"➕ Долито воды: {fmt(r['water_to_add_l'])} л",
        ]
        if r["end_residual_l"] is not None:
            lines.append(f"💧 Остаток после обработки: {fmt(r['end_residual_l'])} л")
        if chemicals[r["id"]]:
            lines.append("🧪 Добавлено химии:")
            for chem in chemicals[r["id"]]:
                lines.append(f"• {chem['chemical_name']} — {fmt(chem['amount'])} {chem['unit']}")
        lines.append(
            "👤 Заправку ввёл: " + actor_label(
                r["entered_by_id"], r["entered_by_name"],
                r["entered_by_role"], known_users
            )
        )
        if r["closed_by_id"] is not None:
            closer = actor_label(
                r["closed_by_id"], r["closed_by_name"],
                r["closed_by_role"], known_users
            )
            if r["closed_by_id"] != r["entered_by_id"]:
                lines.append(f"👤 Результат ввёл: {closer}")
        lines.append("")
    lines += [
        f"🚿 Всего заправок за дату: {len(rows)}",
        f"💧 Долито воды: {fmt(total_water)} л",
        f"🚜 Обработано: {fmt(total_ha)} га",
    ]
    # Длинную историю разбиваем на сообщения в пределах лимита Telegram.
    page = []
    for line in lines:
        if page and len("\n".join(page)) + len(line) + 1 > 3800:
            await update.message.reply_text("\n".join(page))
            page = [f"📚 ЗАПРАВКИ: {field_name} | {date_label(day)} (продолжение)", ""]
        page.append(line)
    await update.message.reply_text("\n".join(page), reply_markup=rows_kb(dates.keys()))


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    uid = update.effective_user.id
    text = update.message.text.strip()
    state = flow.get(uid)
    # План использует справочники только для чтения и не сохраняет даже
    # промежуточные ответы в базу: состояние живёт лишь в памяти процесса.
    if text != BTN_PLAN_JOB and not (state and state.get("mode", "").startswith("plan_")):
        remember_user(update)
    job = active_job(uid)

    admin_edit_modes = {
        "add_filler", "add_culture", "add_chemical_name", "add_chemical_unit",
        "add_field_name", "add_field_area", "add_field_culture",
        "add_tractor_name", "add_tractor_capacity", "edit_tractor_menu",
        "edit_tractor_capacity", "field_culture_select", "field_culture_choose",
    }
    if state and not is_admin(uid) and (
        state.get("table") in ("fields", "cultures", "chemicals", "fillers", "tractors",
                               "tank_volumes", "water_rates")
        or state.get("mode") in admin_edit_modes
    ):
        flow.pop(uid, None)
        await update.message.reply_text("Права администратора больше не доступны.")
        return

    if text == BTN_CANCEL:
        flow.pop(uid, None)
        await update.message.reply_text(
            "Отменено.",
            reply_markup=active_kb(uid) if job else main_kb(uid)
        )
        return

    if text == BTN_BACK:
        if state and state.get("mode") == "history_date":
            await choose_refill_history_field(update)
            return
        flow.pop(uid, None)
        await update.message.reply_text(
            "Главное меню.",
            reply_markup=active_kb(uid) if job else main_kb(uid)
        )
        return

    if text == BTN_PLAN_JOB:
        await begin_plan_job(update)
        return

    if text in (BTN_TANK_VOLUMES, BTN_WATER_RATES):
        if not is_admin(uid):
            await update.message.reply_text("Этот раздел доступен администратору.")
            return
        table = "tank_volumes" if text == BTN_TANK_VOLUMES else "water_rates"
        flow[uid] = {"mode": "numeric_section", "table": table}
        await update.message.reply_text(text, reply_markup=section_kb(table))
        return

    if state and state.get("mode", "").startswith("numeric_"):
        await handle_numeric_section(update, state, text)
        return

    if state and state.get("mode", "").startswith("plan_"):
        await handle_plan_job(update, state, text)
        return

    # ---------- Дополнительные администраторы ----------
    if text == BTN_ADMINS:
        if not is_admin(uid):
            await update.message.reply_text("Этот раздел доступен администраторам.")
            return
        flow[uid] = {"mode": "admins_menu"}
        await update.message.reply_text("👑 Администраторы", reply_markup=admins_kb())
        return

    if state and state.get("mode", "").startswith("admin"):
        if not is_admin(uid):
            flow.pop(uid, None)
            await update.message.reply_text("Права администратора больше не доступны.")
            return
        if state["mode"] == "admins_menu":
            if text == BTN_ADD_ADMIN:
                flow[uid] = {"mode": "admin_add_id"}
                await update.message.reply_text(
                    "Попросите человека открыть личный чат с ботом и отправить /id.\n"
                    "Введите полученный Telegram ID (только цифры):"
                )
                return
            if text == BTN_LIST_ADMINS:
                with db() as c:
                    admins = c.execute(
                        "SELECT user_id,name FROM bot_admins ORDER BY name,user_id"
                    ).fetchall()
                lines = ["👑 АДМИНИСТРАТОРЫ", ""]
                if ADMIN_ID:
                    lines.append(f"• Основной — {ADMIN_ID}")
                for admin in admins:
                    lines.append(f"• {admin['name'] or 'Администратор'} — {admin['user_id']}")
                await update.message.reply_text("\n".join(lines), reply_markup=admins_kb())
                return
            if text == BTN_REMOVE_ADMIN:
                with db() as c:
                    admins = c.execute(
                        "SELECT user_id,name FROM bot_admins ORDER BY name,user_id"
                    ).fetchall()
                if not admins:
                    await update.message.reply_text(
                        "Дополнительных администраторов нет.", reply_markup=admins_kb()
                    )
                    return
                mapping = {
                    f"{a['name'] or 'Администратор'} | ID {a['user_id']}": a["user_id"]
                    for a in admins
                }
                flow[uid] = {"mode": "admin_remove_select", "map": mapping}
                await update.message.reply_text(
                    "Кого удалить из администраторов?", reply_markup=rows_kb(mapping.keys())
                )
                return
        if state["mode"] == "admin_add_id":
            if not text.isdecimal() or int(text) <= 0:
                await update.message.reply_text("Введите Telegram ID цифрами. Его показывает команда /id.")
                return
            new_id = int(text)
            if new_id == ADMIN_ID:
                await update.message.reply_text("Это уже основной администратор.")
                return
            with db() as c:
                exists = c.execute("SELECT 1 FROM bot_admins WHERE user_id=?", (new_id,)).fetchone()
                if not exists:
                    c.execute("INSERT INTO bot_admins(user_id) VALUES(?)", (new_id,))
            flow[uid] = {"mode": "admins_menu"}
            await update.message.reply_text(
                ("Этот человек уже администратор.\n" if exists else "✅ Администратор добавлен.\n")
                + f"Telegram ID: {new_id}\n"
                "Пусть он отправит боту /start в личном чате.",
                reply_markup=admins_kb()
            )
            return
        if state["mode"] == "admin_remove_select" and text in state["map"]:
            flow[uid] = {"mode": "admin_remove_confirm", "id": state["map"][text]}
            await update.message.reply_text(
                f"Удалить права администратора у {text}?",
                reply_markup=keyboard([[BTN_CONFIRM_REMOVE_ADMIN], [BTN_CANCEL]])
            )
            return
        if state["mode"] == "admin_remove_confirm" and text == BTN_CONFIRM_REMOVE_ADMIN:
            with db() as c:
                c.execute("DELETE FROM bot_admins WHERE user_id=?", (state["id"],))
            flow[uid] = {"mode": "admins_menu"} if is_admin(uid) else {}
            await update.message.reply_text(
                "✅ Права администратора удалены.",
                reply_markup=admins_kb() if is_admin(uid) else main_kb(uid)
            )
            return

    if text == BTN_REFILL_HISTORY:
        await choose_refill_history_field(update)
        return

    if state and state.get("mode") == "history_field" and text in state["fields"]:
        await choose_refill_history_date(update, text)
        return

    if state and state.get("mode") == "history_date" and text in state["dates"]:
        await show_refill_history(update, state["field"], state["dates"][text], state["dates"])
        return

    # ---------- Создание новой работы ----------
    if state and state.get("mode") == "job_tractor" and text in state["map"]:
        with db() as c:
            tractor = c.execute(
                "SELECT * FROM tractors WHERE id=? AND active=1", (state["map"][text],)
            ).fetchone()
        if not tractor:
            await update.message.reply_text("Трактор больше не доступен. Выберите другой.")
            return
        await choose_job_field(update, dict(tractor))
        return

    if state and state.get("mode") == "field" and text in state["map"]:
        field_id = state["map"][text]

        with db() as c:
            field = c.execute(
                "SELECT * FROM fields WHERE id=?", (field_id,)
            ).fetchone()
            cultures = [
                r["name"] for r in c.execute(
                    "SELECT name FROM cultures WHERE active=1 ORDER BY name"
                ).fetchall()
            ]

        flow[uid] = {
            "mode": "culture", "field": dict(field), "tractor": state["tractor"]
        }
        await update.message.reply_text(
            "🌱 Выберите культуру:",
            reply_markup=rows_kb(cultures)
        )
        return

    if state and state.get("mode") == "culture":
        with db() as c:
            ok = c.execute(
                "SELECT 1 FROM cultures WHERE active=1 AND name=?",
                (text,)
            ).fetchone()

        if ok:
            state["culture"] = text
            await choose_setting(update, state, "tank_volumes", "tank")
        return

    if state and state.get("mode") == "tank":
        if text not in state["values"]:
            await update.message.reply_text("Выберите объём бака из списка кнопкой.")
            return

        state["tank"] = state["values"][text]
        await choose_setting(update, state, "water_rates", "water_rate")
        return

    if state and state.get("mode") == "water_rate":
        if text not in state["values"]:
            await update.message.reply_text("Выберите расход воды из списка кнопкой.")
            return
        value = state["values"][text]

        field = state["field"]
        actor_id, actor_name, actor_role = entry_actor(update)

        with db() as c:
            cur = c.execute(
                """INSERT INTO jobs(
                    user_id,field_id,field_name,field_area,culture,
                    tank_volume,water_rate,status,started_at,
                    tractor_id,tractor_name,water_capacity_l,
                    entered_by_id,entered_by_name,entered_by_role
                ) VALUES(?,?,?,?,?,?,?,'active',?,?,?,?,?,?,?)""",
                (
                    uid, field["id"], field["name"], field["area"],
                    state["culture"], state["tank"], value,
                    local_now().isoformat(timespec="seconds"),
                    state["tractor"]["id"], state["tractor"]["name"],
                    state["tractor"]["water_capacity_l"],
                    actor_id, actor_name, actor_role
                )
            )
            job_id = cur.lastrowid

        await choose_chemical(update, job_id)
        return

    # ---------- Рецепт ----------
    if state and state.get("mode") == "chem" and text in state["map"]:
        chem_id = state["map"][text]

        with db() as c:
            chem = c.execute(
                "SELECT * FROM chemicals WHERE id=?", (chem_id,)
            ).fetchone()

        state["chem"] = dict(chem)
        state["mode"] = "chem_rate"

        await update.message.reply_text(
            f"🧪 {chem['name']}\n"
            f"Введите норму на 1 га ({chem['unit']}/га):"
        )
        return

    if state and state.get("mode") == "chem_rate":
        value = number(text)
        if value is None or value < 0:
            await update.message.reply_text("Введите норму числом.")
            return

        chem = state["chem"]

        with db() as c:
            c.execute(
                """INSERT INTO recipes(
                    job_id,chemical_id,chemical_name,unit,rate_per_ha
                ) VALUES(?,?,?,?,?)""",
                (
                    state["job_id"], chem["id"], chem["name"],
                    chem["unit"], value
                )
            )

        state["mode"] = "chem_more"
        await update.message.reply_text(
            "✅ Препарат добавлен.",
            reply_markup=keyboard([
                [BTN_ADD_CHEM, BTN_CHEM_DONE],
                [BTN_CANCEL]
            ])
        )
        return

    if state and state.get("mode") == "chem_more":
        if text == BTN_ADD_CHEM:
            await choose_chemical(update, state["job_id"])
            return

        if text == BTN_CHEM_DONE:
            job_id = state["job_id"]
            flow[uid] = {"mode": "first_residual", "job_id": job_id}
            await update.message.reply_text(
                "✅ Рецепт сохранён.\n\n"
                "Первая заправка.\n"
                "💧 Сколько сейчас осталось воды/раствора в баке?\n"
                "Если бак пустой — введите 0."
            )
            return

    # ---------- Остаток перед полной заправкой ----------
    if state and state.get("mode") in ("first_residual", "full_residual"):
        residual = number(text)

        if residual is None or residual < 0:
            await update.message.reply_text("Введите остаток в литрах.")
            return

        job = active_job(uid)
        if residual > job["tank_volume"]:
            await update.message.reply_text(
                f"Объём бака {fmt(job['tank_volume'])} л. "
                "Остаток не может быть больше."
            )
            return

        closed = close_previous_refill(job, residual, update)
        if closed and closed.get("error"):
            await update.message.reply_text(closed["error"])
            return
        if closed:
            with db() as c:
                total_done = c.execute(
                    "SELECT COALESCE(SUM(actual_sprayed_ha),0) s FROM refills WHERE job_id=?",
                    (job["id"],)
                ).fetchone()["s"]
            left = max(0.0, job["field_area"] - total_done)
            await update.message.reply_text(
                f"✅ Предыдущая заправка №{closed['seq']} завершена.\n"
                f"🚜 За заправку: {fmt(closed['actual_ha'])} га\n"
                f"📊 Всего обработано: {fmt(total_done)} га\n"
                f"🌾 Осталось обработать: {fmt(left)} га\n"
                f"💧 Использовано раствора: {fmt(closed['used_l'])} л\n"
                f"💧 Остаток: {fmt(residual)} л"
            )

        await choose_filler(update, "full", None, residual)
        return

    # ---------- Заправка на конкретную площадь ----------
    if state and state.get("mode") == "partial_area":
        area = number(text)

        if not area or area <= 0:
            await update.message.reply_text("Введите площадь числом, например 7.")
            return

        job = active_job(uid)
        state["area"] = area
        state["mode"] = "partial_residual"

        await update.message.reply_text(
            f"🎯 Нужно обработать: {fmt(area)} га\n"
            f"💧 При норме {fmt(job['water_rate'])} л/га "
            f"нужно всего {fmt(area * job['water_rate'])} л раствора.\n\n"
            "💧 Сколько сейчас осталось в баке, л?"
        )
        return

    if state and state.get("mode") == "partial_residual":
        residual = number(text)

        if residual is None or residual < 0:
            await update.message.reply_text("Введите остаток в литрах.")
            return

        job = active_job(uid)
        area = state["area"]
        required = area * job["water_rate"]

        if residual > required:
            await update.message.reply_text(
                f"Для {fmt(area)} га нужно всего {fmt(required)} л. "
                f"Вы ввели остаток {fmt(residual)} л.\n"
                "Проверьте остаток или укажите большую площадь."
            )
            return

        closed = close_previous_refill(job, residual, update)
        if closed and closed.get("error"):
            await update.message.reply_text(closed["error"])
            return
        if closed:
            with db() as c:
                total_done = c.execute(
                    "SELECT COALESCE(SUM(actual_sprayed_ha),0) s FROM refills WHERE job_id=?",
                    (job["id"],)
                ).fetchone()["s"]
            left = max(0.0, job["field_area"] - total_done)
            await update.message.reply_text(
                f"✅ Предыдущая заправка №{closed['seq']} завершена.\n"
                f"🚜 За заправку: {fmt(closed['actual_ha'])} га\n"
                f"📊 Всего обработано: {fmt(total_done)} га\n"
                f"🌾 Осталось обработать: {fmt(left)} га\n"
                f"💧 Использовано раствора: {fmt(closed['used_l'])} л\n"
                f"💧 Остаток: {fmt(residual)} л"
            )

        await choose_filler(update, "partial", area, residual)
        return

    # ---------- Выбор заправщика ----------
    if state and state.get("mode") == "filler":
        if text not in state["fillers"]:
            return

        job = active_job(uid)
        refill_type = state["refill_type"]
        target_ha = state["target_ha"]
        residual = state["residual"]

        flow.pop(uid, None)

        await save_refill(
            update, job, refill_type, target_ha, residual, text
        )
        return

    # ---------- Изменение / удаление справочников ----------
    if state and state.get("mode") == "crud_select" and text in state["map"]:
        item_id = state["map"][text]
        table = state["table"]

        if state["action"] == "delete":
            with db() as c:
                c.execute(f"UPDATE {table} SET active=0 WHERE id=?", (item_id,))
            flow[uid] = {"mode": "section", "table": table}
            await update.message.reply_text(
                "🗑 Удалено из активного списка. История работ сохранена.",
                reply_markup=section_kb(table)
            )
            return

        with db() as c:
            row = c.execute(f"SELECT * FROM {table} WHERE id=?", (item_id,)).fetchone()

        flow[uid] = {
            "mode": "crud_edit_name",
            "table": table,
            "id": item_id,
            "old": dict(row)
        }
        if table == "tractors":
            flow[uid]["mode"] = "edit_tractor_menu"
            await update.message.reply_text(
                f"🚜 {row['name']} | Бочка {fmt(row['water_capacity_l'])} л\n"
                "Что изменить?",
                reply_markup=rows_kb(["Название", "Объём бочки"])
            )
            return
        await update.message.reply_text(
            f"✏️ Текущее название: {row['name']}\\n"
            "Введите новое название:"
        )
        return

    if state and state.get("mode") == "edit_tractor_menu":
        if text == "Название":
            state["mode"] = "crud_edit_name"
            await update.message.reply_text("Введите новое название трактора:")
        elif text == "Объём бочки":
            state["mode"] = "edit_tractor_capacity"
            await update.message.reply_text("Введите новый объём бочки в литрах:")
        else:
            await update.message.reply_text("Выберите, что изменить, кнопкой.")
        return

    if state and state.get("mode") == "edit_tractor_capacity":
        value = number(text)
        if value is None or not math.isfinite(value) or value <= 0:
            await update.message.reply_text("Введите положительный объём в литрах, например 6500.")
            return
        with db() as c:
            c.execute("UPDATE tractors SET water_capacity_l=? WHERE id=?", (value, state["id"]))
        flow[uid] = {"mode": "section", "table": "tractors"}
        await update.message.reply_text(
            f"✅ Объём бочки изменён: {fmt(value)} л.",
            reply_markup=section_kb("tractors")
        )
        return

    if state and state.get("mode") == "add_tractor_name":
        if not text:
            await update.message.reply_text("Введите название трактора.")
            return
        state["name"] = text
        state["mode"] = "add_tractor_capacity"
        await update.message.reply_text("Введите объём перевозимой воды в литрах, например 6500:")
        return

    if state and state.get("mode") == "add_tractor_capacity":
        value = number(text)
        if value is None or not math.isfinite(value) or value <= 0:
            await update.message.reply_text("Введите положительный объём в литрах, например 6500.")
            return
        with db() as c:
            try:
                c.execute(
                    "INSERT INTO tractors(name,water_capacity_l) VALUES(?,?)",
                    (state["name"], value)
                )
            except sqlite3.IntegrityError:
                c.execute(
                    "UPDATE tractors SET active=1,water_capacity_l=? WHERE name=?",
                    (value, state["name"])
                )
        flow[uid] = {"mode": "section", "table": "tractors"}
        await update.message.reply_text(
            f"✅ Трактор сохранён: {state['name']}, бочка {fmt(value)} л.",
            reply_markup=section_kb("tractors")
        )
        return

    if state and state.get("mode") == "field_culture_select" and text in state["map"]:
        field_id = state["map"][text]
        with db() as c:
            field = c.execute(
                "SELECT id,name,area,culture FROM fields WHERE id=? AND active=1",
                (field_id,)
            ).fetchone()
            cultures = [r["name"] for r in c.execute(
                "SELECT name FROM cultures WHERE active=1 ORDER BY name"
            ).fetchall()]
        if not field:
            flow[uid] = {"mode": "section", "table": "fields"}
            await update.message.reply_text(
                "Поле больше не доступно.", reply_markup=section_kb("fields")
            )
            return
        flow[uid] = {"mode": "field_culture_choose", "field": dict(field)}
        await update.message.reply_text(
            f"🌾 Поле: {field['name']}\n"
            f"Текущая культура: {field['culture']}\n\n"
            "Выберите новую культуру:",
            reply_markup=rows_kb(cultures)
        )
        return

    if state and state.get("mode") == "field_culture_choose":
        with db() as c:
            culture = c.execute(
                "SELECT 1 FROM cultures WHERE name=? AND active=1", (text,)
            ).fetchone()
            if not culture:
                await update.message.reply_text("Выберите культуру из списка.")
                return
            field = state["field"]
            changed = c.execute(
                "UPDATE fields SET culture=? WHERE id=? AND active=1",
                (text, field["id"])
            ).rowcount
        flow[uid] = {"mode": "section", "table": "fields"}
        if not changed:
            await update.message.reply_text(
                "Поле больше не доступно.", reply_markup=section_kb("fields")
            )
            return
        await update.message.reply_text(
            f"✅ Культура изменена.\n"
            f"🌾 {field['name']}\n"
            f"{field['culture']} → {text}\n"
            f"Площадь: {fmt(field['area'])} га",
            reply_markup=section_kb("fields")
        )
        return

    if state and state.get("mode") == "crud_edit_name":
        table = state["table"]
        item_id = state["id"]

        if table == "fields":
            state["new_name"] = text
            state["mode"] = "crud_edit_field_area"
            await update.message.reply_text(
                f"Текущая площадь: {fmt(state['old']['area'])} га\\n"
                "Введите новую площадь:"
            )
            return

        if table == "chemicals":
            state["new_name"] = text
            state["mode"] = "crud_edit_chem_unit"
            await update.message.reply_text(
                f"Текущая единица: {state['old']['unit']}\\n"
                "Введите новую единицу (обычно л):"
            )
            return

        with db() as c:
            try:
                c.execute(f"UPDATE {table} SET name=? WHERE id=?", (text, item_id))
            except sqlite3.IntegrityError:
                await update.message.reply_text("Такое название уже существует.")
                return
        flow[uid] = {"mode": "section", "table": table}
        await update.message.reply_text("✅ Изменено.", reply_markup=section_kb(table))
        return

    if state and state.get("mode") == "crud_edit_field_area":
        area = number(text)
        if not area or area <= 0:
            await update.message.reply_text("Введите площадь числом.")
            return
        state["new_area"] = area
        with db() as c:
            cultures = [r["name"] for r in c.execute(
                "SELECT name FROM cultures WHERE active=1 ORDER BY name"
            ).fetchall()]
        state["mode"] = "crud_edit_field_culture"
        await update.message.reply_text(
            f"Текущая культура: {state['old']['culture']}\\n"
            "Выберите новую культуру:",
            reply_markup=rows_kb(cultures)
        )
        return

    if state and state.get("mode") == "crud_edit_field_culture":
        with db() as c:
            if not c.execute(
                "SELECT 1 FROM cultures WHERE name=? AND active=1", (text,)
            ).fetchone():
                await update.message.reply_text("Выберите культуру из списка.")
                return
            try:
                c.execute(
                    "UPDATE fields SET name=?,area=?,culture=? WHERE id=?",
                    (state["new_name"], state["new_area"], text, state["id"])
                )
            except sqlite3.IntegrityError:
                await update.message.reply_text("Поле с таким названием уже существует.")
                return
        flow[uid] = {"mode": "section", "table": "fields"}
        await update.message.reply_text("✅ Поле изменено.", reply_markup=section_kb("fields"))
        return

    if state and state.get("mode") == "crud_edit_chem_unit":
        with db() as c:
            try:
                c.execute(
                    "UPDATE chemicals SET name=?,unit=? WHERE id=?",
                    (state["new_name"], text, state["id"])
                )
            except sqlite3.IntegrityError:
                await update.message.reply_text("Такой препарат уже существует.")
                return
        flow[uid] = {"mode": "section", "table": "chemicals"}
        await update.message.reply_text("✅ Препарат изменён.", reply_markup=section_kb())
        return

    # ---------- Добавление справочников ----------
    if state and state.get("mode") == "add_filler":
        with db() as c:
            try:
                c.execute("INSERT INTO fillers(name) VALUES(?)", (text,))
            except sqlite3.IntegrityError:
                c.execute(
                    "UPDATE fillers SET active=1 WHERE name=?", (text,)
                )
        flow.pop(uid, None)
        await update.message.reply_text("✅ Заправщик добавлен.", reply_markup=section_kb())
        return

    if state and state.get("mode") == "add_culture":
        with db() as c:
            try:
                c.execute("INSERT INTO cultures(name) VALUES(?)", (text,))
            except sqlite3.IntegrityError:
                c.execute(
                    "UPDATE cultures SET active=1 WHERE name=?", (text,)
                )
        flow.pop(uid, None)
        await update.message.reply_text("✅ Культура добавлена.", reply_markup=section_kb())
        return

    if state and state.get("mode") == "add_chemical_name":
        state["name"] = text
        state["mode"] = "add_chemical_unit"
        await update.message.reply_text(
            "Введите единицу препарата.\nОбычно: л"
        )
        return

    if state and state.get("mode") == "add_chemical_unit":
        with db() as c:
            try:
                c.execute(
                    "INSERT INTO chemicals(name,unit) VALUES(?,?)",
                    (state["name"], text)
                )
            except sqlite3.IntegrityError:
                c.execute(
                    "UPDATE chemicals SET active=1,unit=? WHERE name=?",
                    (text, state["name"])
                )
        flow.pop(uid, None)
        await update.message.reply_text("✅ Препарат добавлен.", reply_markup=section_kb())
        return

    if state and state.get("mode") == "add_field_name":
        state["name"] = text
        state["mode"] = "add_field_area"
        await update.message.reply_text("Введите площадь поля, га:")
        return

    if state and state.get("mode") == "add_field_area":
        area = number(text)
        if not area or area <= 0:
            await update.message.reply_text("Введите площадь числом.")
            return

        state["area"] = area

        with db() as c:
            cultures = [
                r["name"] for r in c.execute(
                    "SELECT name FROM cultures WHERE active=1 ORDER BY name"
                ).fetchall()
            ]

        state["mode"] = "add_field_culture"
        await update.message.reply_text(
            "Выберите текущую культуру поля:",
            reply_markup=rows_kb(cultures)
        )
        return

    if state and state.get("mode") == "add_field_culture":
        with db() as c:
            try:
                c.execute(
                    "INSERT INTO fields(name,area,culture) VALUES(?,?,?)",
                    (state["name"], state["area"], text)
                )
            except sqlite3.IntegrityError:
                c.execute(
                    "UPDATE fields SET active=1,area=?,culture=? WHERE name=?",
                    (state["area"], text, state["name"])
                )

        flow.pop(uid, None)
        await update.message.reply_text("✅ Поле добавлено.", reply_markup=section_kb("fields"))
        return

    # ---------- Итоги: выбор активной даты / поля ----------
    if state and state.get("mode") == "report_date" and text in state["map"]:
        d = state["map"][text]
        flow.pop(uid, None)
        await send_report(
            update,
            " AND substr(j.started_at,1,10)=?",
            (d,),
            f"🔎 ИТОГ ЗА {text}"
        )
        return

    if state and state.get("mode") == "report_field" and text in state["fields"]:
        flow.pop(uid, None)
        await send_report(
            update,
            " AND j.field_name=?",
            (text,),
            f"🌾 ИТОГ ПО ПОЛЮ: {text}"
        )
        return

    # ---------- Завершение: остаток последней заправки ----------
    if state and state.get("mode") == "finish_residual":
        residual = number(text)
        if residual is None or residual < 0:
            await update.message.reply_text("Введите остаток в литрах.")
            return

        job = active_job(uid)
        closed = close_previous_refill(job, residual, update)
        if closed and closed.get("error"):
            await update.message.reply_text(closed["error"])
            return

        with db() as c:
            c.execute(
                "UPDATE jobs SET status='done',finished_at=? WHERE id=?",
                (local_now().isoformat(timespec="seconds"), job["id"])
            )
            actual_ha = c.execute(
                "SELECT COALESCE(SUM(actual_sprayed_ha),0) s FROM refills WHERE job_id=?",
                (job["id"],)
            ).fetchone()["s"]
            recipe = c.execute(
                "SELECT chemical_name,unit,rate_per_ha FROM recipes WHERE job_id=? ORDER BY id",
                (job["id"],)
            ).fetchall()

        lines = [
            "✅ РАБОТА ПО ПОЛЮ ЗАВЕРШЕНА",
            "",
            f"🌾 Поле: {job['field_name']}",
            f"🌱 Культура: {job['culture']}",
            f"🚜 Фактически обработано: {fmt(actual_ha)} га",
            f"💧 Остаток в опрыскивателе: {fmt(residual)} л",
            "",
            "🧪 ФАКТИЧЕСКИ ПОШЛО НА ПОЛЕ:"
        ]
        for r in recipe:
            lines.append(
                f"• {r['chemical_name']} — "
                f"{fmt(actual_ha * r['rate_per_ha'])} {r['unit']}"
            )

        flow.pop(uid, None)
        await update.message.reply_text("\n".join(lines), reply_markup=main_kb(uid))
        return

    # ---------- Основные кнопки ----------
    if text == BTN_NEW:
        if job:
            await update.message.reply_text(
                "Сначала завершите текущее поле.",
                reply_markup=active_kb(uid)
            )
        else:
            await begin_job(update)
        return

    if text == BTN_NEXT and job:
        flow[uid] = {"mode": "full_residual"}
        await update.message.reply_text(
            "🚿 СЛЕДУЮЩАЯ ЗАПРАВКА\n\n"
            "💧 Сколько воды/раствора осталось в баке, л?"
        )
        return

    if text == BTN_PARTIAL and job:
        flow[uid] = {"mode": "partial_area"}
        await update.message.reply_text(
            "🎯 ЗАПРАВКА НА ПЛОЩАДЬ\n\n"
            "Сколько гектаров нужно обработать?\n"
            "Например: 7"
        )
        return

    if text == BTN_TOTAL and job:
        await show_total(update, job)
        return

    if text == BTN_PLANNED_REFILLS and job:
        with db() as c:
            recipe = c.execute(
                "SELECT chemical_name,unit,rate_per_ha FROM recipes WHERE job_id=? ORDER BY id",
                (job["id"],)
            ).fetchall()
            done = c.execute(
                "SELECT COUNT(*) n FROM refills WHERE job_id=?", (job["id"],)
            ).fetchone()["n"]
        lines = planned_refills(job) + ["", f"✅ Уже сделано заправок: {done}"]
        if recipe:
            lines += ["", "🧪 ХИМИЯ НА ВСЁ ПОЛЕ:"]
            for r in recipe:
                lines.append(
                    f"• {r['chemical_name']}: {fmt(r['rate_per_ha'])} {r['unit']}/га"
                    f" → {fmt(float(job['field_area']) * r['rate_per_ha'])} {r['unit']}"
                )
        await update.message.reply_text("\n".join(lines), reply_markup=active_kb(uid))
        return

    if text == BTN_FINISH and job:
        flow[uid] = {"mode": "finish_residual"}
        await update.message.reply_text(
            "✅ ЗАВЕРШЕНИЕ ПОЛЯ\n\n"
            "💧 Сколько раствора осталось в опрыскивателе, л?\n"
            "Если бак пустой — введите 0."
        )
        return

    # ---------- Исправить последнее показание ----------
    if text == BTN_CORRECT_LAST:
        with db() as c:
            last = c.execute(
                """SELECT r.*, j.field_name, j.field_area, j.water_rate, j.id job_id
                   FROM refills r JOIN jobs j ON j.id=r.job_id
                   WHERE r.end_residual_l IS NOT NULL
                   ORDER BY COALESCE(r.closed_at,r.created_at) DESC, r.id DESC
                   LIMIT 1"""
            ).fetchone()
        if not last:
            await update.message.reply_text("Нет завершённой заправки, которую можно исправить.")
            return
        flow[uid] = {
            "mode": "correct_last_residual",
            "refill_id": last["id"],
            "job_id": last["job_id"],
            "max_l": float(last["total_solution_l"])
        }
        await update.message.reply_text(
            f"✏️ ИСПРАВИТЬ ПОСЛЕДНЕЕ\n\n"
            f"🌾 Поле: {last['field_name']}\n"
            f"🚿 Заправка №{last['seq']}\n"
            f"💧 Сейчас записан остаток: {fmt(last['end_residual_l'])} л\n\n"
            "Введите правильный остаток в литрах:"
        )
        return

    if state and state.get("mode") == "correct_last_residual":
        residual = number(text)
        if residual is None or residual < 0:
            await update.message.reply_text("Введите правильный остаток числом.")
            return
        if residual > state["max_l"] + 0.0001:
            await update.message.reply_text(
                f"Остаток не может быть больше {fmt(state['max_l'])} л."
            )
            return
        with db() as c:
            actor_id, actor_name, actor_role = entry_actor(update)
            c.execute(
                """UPDATE refills SET end_residual_l=?,closed_by_id=?,
                   closed_by_name=?,closed_by_role=? WHERE id=?""",
                (residual, actor_id, actor_name, actor_role, state["refill_id"])
            )
        recalc_job_actuals(state["job_id"])
        job, total, recipe = job_summary(state["job_id"])
        left = max(0.0, float(job["field_area"]) - total)
        lines = [
            "✅ ПОКАЗАНИЕ ИСПРАВЛЕНО",
            "",
            f"🌾 Поле: {job['field_name']}",
            f"📊 Всего обработано: {fmt(total)} га",
            f"🌾 Осталось обработать: {fmt(left)} га",
            f"💧 Исправленный остаток: {fmt(residual)} л",
            "",
            "🧪 Фактический расход химии:"
        ]
        for r in recipe:
            lines.append(
                f"• {r['chemical_name']} — {fmt(total * r['rate_per_ha'])} {r['unit']}"
            )
        flow.pop(uid, None)
        await update.message.reply_text("\n".join(lines), reply_markup=main_kb(uid))
        return

    # ---------- Удалить конкретную работу ----------
    if text == BTN_DELETE_JOB:
        today = local_now().strftime("%Y-%m-%d")
        with db() as c:
            rows = c.execute(
                """SELECT j.id,j.field_name,j.started_at,
                          COALESCE(SUM(r.actual_sprayed_ha),0) actual_ha
                   FROM jobs j
                   LEFT JOIN refills r ON r.job_id=j.id
                   WHERE substr(j.started_at,1,10)=?
                   GROUP BY j.id
                   ORDER BY j.started_at DESC,j.id DESC""",
                (today,)
            ).fetchall()
        if not rows:
            await update.message.reply_text("За сегодня работ для удаления нет.")
            return
        mapping = {}
        for r in rows:
            try:
                tm = datetime.fromisoformat(r["started_at"]).strftime("%H:%M")
            except Exception:
                tm = ""
            label = f"{r['field_name']} | {fmt(r['actual_ha'])} га | {tm}"
            mapping[label] = r["id"]
        flow[uid] = {"mode": "delete_job_select", "map": mapping}
        await update.message.reply_text(
            "🗑 Выберите работу за сегодня, которую нужно удалить:",
            reply_markup=rows_kb(mapping.keys())
        )
        return

    if state and state.get("mode") == "delete_job_select" and text in state["map"]:
        job_id = state["map"][text]
        flow[uid] = {"mode": "delete_job_confirm", "job_id": job_id, "label": text}
        await update.message.reply_text(
            f"⚠️ Удалить эту работу полностью?\n\n{text}\n\n"
            "Будут удалены её заправки и расчёты химии.",
            reply_markup=keyboard([[BTN_CONFIRM_DELETE], [BTN_CANCEL_DELETE]])
        )
        return

    if state and state.get("mode") == "delete_job_confirm":
        if text == BTN_CANCEL_DELETE:
            flow.pop(uid, None)
            await update.message.reply_text("Удаление отменено.", reply_markup=main_kb(uid))
            return
        if text == BTN_CONFIRM_DELETE:
            job_id = state["job_id"]
            with db() as c:
                refill_ids = [r["id"] for r in c.execute(
                    "SELECT id FROM refills WHERE job_id=?", (job_id,)
                ).fetchall()]
                if refill_ids:
                    marks = ",".join("?" for _ in refill_ids)
                    c.execute(f"DELETE FROM refill_chemicals WHERE refill_id IN ({marks})", refill_ids)
                c.execute("DELETE FROM refills WHERE job_id=?", (job_id,))
                c.execute("DELETE FROM recipes WHERE job_id=?", (job_id,))
                c.execute("DELETE FROM jobs WHERE id=?", (job_id,))
            flow.pop(uid, None)
            await update.message.reply_text(
                "🗑 Работа полностью удалена. Поля, культуры, химия и заправщики сохранены.",
                reply_markup=main_kb(uid)
            )
            return

    # ---------- Итоги ----------
    if text == BTN_REPORTS:
        flow[uid] = {"mode": "reports"}
        await update.message.reply_text("📊 ИТОГИ", reply_markup=reports_kb())
        return

    if state and state.get("mode") == "reports":
        if text == BTN_TODAY:
            today = local_now().strftime("%Y-%m-%d")
            await send_report(
                update,
                " AND substr(j.started_at,1,10)=?",
                (today,),
                "📆 ИТОГ ЗА СЕГОДНЯ"
            )
            return
        if text == BTN_BY_DATE:
            await choose_report_date(update)
            return
        if text == BTN_BY_FIELD:
            await choose_report_field(update)
            return
        if text == BTN_SEASON:
            await send_report(update, "", (), "🏆 ИТОГ ЗА СЕЗОН")
            return

    # ---------- Админ-справочники ----------
    if text in (BTN_FIELDS, BTN_CULTURES, BTN_CHEM, BTN_FILLERS, BTN_TRACTORS):
        if not is_admin(uid):
            await update.message.reply_text("Этот раздел доступен администратору.")
            return

        table = {
            BTN_FIELDS: "fields",
            BTN_CULTURES: "cultures",
            BTN_CHEM: "chemicals",
            BTN_FILLERS: "fillers",
            BTN_TRACTORS: "tractors",
        }[text]

        flow[uid] = {"mode": "section", "table": table}
        await update.message.reply_text(text, reply_markup=section_kb(table))
        return

    if state and state.get("mode") == "section":
        table = state["table"]

        if table == "fields" and text == BTN_EDIT_CULTURE:
            with db() as c:
                rs = c.execute(
                    "SELECT id,name,area,culture FROM fields WHERE active=1 ORDER BY name"
                ).fetchall()
            mapping = {
                f"🌾 {r['name']} | {r['culture']} | {fmt(r['area'])} га": r["id"]
                for r in rs
            }
            flow[uid] = {"mode": "field_culture_select", "map": mapping}
            await update.message.reply_text(
                "Выберите поле, у которого нужно изменить культуру:",
                reply_markup=rows_kb(mapping.keys())
            )
            return

        if text == BTN_LIST:
            with db() as c:
                if table == "fields":
                    rs = c.execute(
                        "SELECT name,area,culture FROM fields "
                        "WHERE active=1 ORDER BY name"
                    ).fetchall()
                    lines = [
                        f"• {r['name']} | {r['culture']} | {fmt(r['area'])} га"
                        for r in rs
                    ]
                elif table == "chemicals":
                    rs = c.execute(
                        "SELECT name,unit FROM chemicals "
                        "WHERE active=1 ORDER BY name"
                    ).fetchall()
                    lines = [f"• {r['name']} | {r['unit']}" for r in rs]
                elif table == "tractors":
                    rs = c.execute(
                        "SELECT name,water_capacity_l FROM tractors "
                        "WHERE active=1 ORDER BY name"
                    ).fetchall()
                    lines = [
                        f"• {r['name']} | Бочка {fmt(r['water_capacity_l'])} л"
                        for r in rs
                    ]
                else:
                    rs = c.execute(
                        f"SELECT name FROM {table} WHERE active=1 ORDER BY name"
                    ).fetchall()
                    lines = [f"• {r['name']}" for r in rs]

            await update.message.reply_text(
                "📋 СПИСОК\n\n" + ("\n".join(lines) if lines else "Список пуст."),
                reply_markup=section_kb(table)
            )
            return

        if text in (BTN_EDIT, BTN_DELETE):
            with db() as c:
                if table == "fields":
                    rs = c.execute("SELECT id,name FROM fields WHERE active=1 ORDER BY name").fetchall()
                else:
                    rs = c.execute(f"SELECT id,name FROM {table} WHERE active=1 ORDER BY name").fetchall()
            mapping = {r["name"]: r["id"] for r in rs}
            flow[uid] = {
                "mode": "crud_select",
                "table": table,
                "action": "edit" if text == BTN_EDIT else "delete",
                "map": mapping
            }
            await update.message.reply_text(
                "Что изменить?" if text == BTN_EDIT else "Что удалить?",
                reply_markup=rows_kb(mapping.keys())
            )
            return

        if text == BTN_ADD:
            if table == "tractors":
                flow[uid] = {"mode": "add_tractor_name"}
                prompt = "Введите название трактора:"
            elif table == "fillers":
                flow[uid] = {"mode": "add_filler"}
                prompt = "Введите имя заправщика:"
            elif table == "cultures":
                flow[uid] = {"mode": "add_culture"}
                prompt = "Введите название культуры:"
            elif table == "chemicals":
                flow[uid] = {"mode": "add_chemical_name"}
                prompt = "Введите название препарата:"
            else:
                flow[uid] = {"mode": "add_field_name"}
                prompt = "Введите название поля:"

            await update.message.reply_text(prompt)
            return

    await update.message.reply_text(
        "Выберите действие кнопкой.",
        reply_markup=active_kb(uid) if job else main_kb(uid)
    )


def main():
    if not TOKEN:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")

    init_db()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", whoami))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle)
    )
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
