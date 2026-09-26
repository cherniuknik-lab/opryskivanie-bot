import os
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
BTN_REPORTS = "📊 Итоги"
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
BTN_FINISH = "✅ Завершить поле"

BTN_FIELDS = "🌾 Поля"
BTN_CULTURES = "🌱 Культуры"
BTN_CHEM = "🧪 Химия"
BTN_FILLERS = "👤 Заправщики"

BTN_ADD = "➕ Добавить"
BTN_EDIT = "✏️ Изменить"
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


def keyboard(rows):
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def main_kb():
    return keyboard([
        [BTN_NEW, BTN_REPORTS],
        [BTN_CORRECT_LAST, BTN_DELETE_JOB],
        [BTN_FIELDS, BTN_CULTURES],
        [BTN_CHEM, BTN_FILLERS],
    ])


def active_kb():
    return keyboard([
        [BTN_NEXT, BTN_PARTIAL],
        [BTN_TOTAL, BTN_REPORTS],
        [BTN_FINISH],
    ])


def section_kb():
    return keyboard([[BTN_ADD, BTN_EDIT], [BTN_DELETE, BTN_LIST], [BTN_BACK]])


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
        refill_cols = {r["name"] for r in c.execute("PRAGMA table_info(refills)").fetchall()}
        for col, ddl in [
            ("end_residual_l", "REAL"),
            ("actual_sprayed_ha", "REAL"),
            ("closed_at", "TEXT"),
        ]:
            if col not in refill_cols:
                c.execute(f"ALTER TABLE refills ADD COLUMN {col} {ddl}")

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job = active_job(update.effective_user.id)
    await update.message.reply_text(
        "🚿 ОПРЫСКИВАНИЕ\n\n"
        + ("Есть активная работа." if job else "Готов к работе."),
        reply_markup=active_kb() if job else main_kb()
    )


async def begin_job(update):
    uid = update.effective_user.id
    with db() as c:
        rs = c.execute(
            "SELECT id,name,area FROM fields WHERE active=1 ORDER BY name"
        ).fetchall()

    mapping = {f"🌾 {r['name']} | {fmt(r['area'])} га": r["id"] for r in rs}
    flow[uid] = {"mode": "field", "map": mapping}

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


def close_previous_refill(job, residual):
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

        c.execute(
            """UPDATE refills
               SET end_residual_l=?, actual_sprayed_ha=?, closed_at=?
               WHERE id=?""",
            (
                residual, actual_ha,
                local_now().isoformat(timespec="seconds"),
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
            reply_markup=active_kb()
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
        seq = c.execute(
            "SELECT COALESCE(MAX(seq),0)+1 n FROM refills WHERE job_id=?",
            (job["id"],)
        ).fetchone()["n"]

        cur = c.execute(
            """INSERT INTO refills(
                job_id,seq,refill_type,target_ha,residual_l,
                total_solution_l,water_to_add_l,filler_name,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                job["id"], seq, refill_type, target_ha, residual,
                total_solution, water_to_add, filler,
                local_now().isoformat(timespec="seconds")
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

    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=active_kb()
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
        reply_markup=active_kb()
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
            ""
        ]
    lines.append(f"📊 ВСЕГО: {fmt(total)} га")
    await update.message.reply_text("\n".join(lines), reply_markup=reports_kb())


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


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    uid = update.effective_user.id
    text = update.message.text.strip()
    state = flow.get(uid)
    job = active_job(uid)

    if text == BTN_CANCEL:
        flow.pop(uid, None)
        await update.message.reply_text(
            "Отменено.",
            reply_markup=active_kb() if job else main_kb()
        )
        return

    if text == BTN_BACK:
        flow.pop(uid, None)
        await update.message.reply_text(
            "Главное меню.",
            reply_markup=active_kb() if job else main_kb()
        )
        return

    # ---------- Создание новой работы ----------
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

        flow[uid] = {"mode": "culture", "field": dict(field)}
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
            state["mode"] = "tank"
            await update.message.reply_text(
                "💧 Введите объём полного опрыскивателя, л.\n"
                "Например: 3000"
            )
        return

    if state and state.get("mode") == "tank":
        value = number(text)
        if not value or value <= 0:
            await update.message.reply_text("Введите объём числом, например 3000.")
            return

        state["tank"] = value
        state["mode"] = "water_rate"
        await update.message.reply_text(
            "💧 Введите норму воды, л/га.\nНапример: 110"
        )
        return

    if state and state.get("mode") == "water_rate":
        value = number(text)
        if not value or value <= 0:
            await update.message.reply_text("Введите норму числом, например 110.")
            return

        field = state["field"]

        with db() as c:
            cur = c.execute(
                """INSERT INTO jobs(
                    user_id,field_id,field_name,field_area,culture,
                    tank_volume,water_rate,status,started_at
                ) VALUES(?,?,?,?,?,?,?,'active',?)""",
                (
                    uid, field["id"], field["name"], field["area"],
                    state["culture"], state["tank"], value,
                    local_now().isoformat(timespec="seconds")
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

        closed = close_previous_refill(job, residual)
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

        closed = close_previous_refill(job, residual)
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
                reply_markup=section_kb()
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
        await update.message.reply_text(
            f"✏️ Текущее название: {row['name']}\\n"
            "Введите новое название:"
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
        await update.message.reply_text("✅ Изменено.", reply_markup=section_kb())
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
            try:
                c.execute(
                    "UPDATE fields SET name=?,area=?,culture=? WHERE id=?",
                    (state["new_name"], state["new_area"], text, state["id"])
                )
            except sqlite3.IntegrityError:
                await update.message.reply_text("Поле с таким названием уже существует.")
                return
        flow[uid] = {"mode": "section", "table": "fields"}
        await update.message.reply_text("✅ Поле изменено.", reply_markup=section_kb())
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
        await update.message.reply_text("✅ Поле добавлено.", reply_markup=section_kb())
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
        closed = close_previous_refill(job, residual)
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
        await update.message.reply_text("\n".join(lines), reply_markup=main_kb())
        return

    # ---------- Основные кнопки ----------
    if text == BTN_NEW:
        if job:
            await update.message.reply_text(
                "Сначала завершите текущее поле.",
                reply_markup=active_kb()
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
            c.execute(
                "UPDATE refills SET end_residual_l=? WHERE id=?",
                (residual, state["refill_id"])
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
        await update.message.reply_text("\n".join(lines), reply_markup=main_kb())
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
            await update.message.reply_text("Удаление отменено.", reply_markup=main_kb())
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
                reply_markup=main_kb()
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
    if text in (BTN_FIELDS, BTN_CULTURES, BTN_CHEM, BTN_FILLERS):
        if uid != ADMIN_ID:
            await update.message.reply_text("Этот раздел доступен администратору.")
            return

        table = {
            BTN_FIELDS: "fields",
            BTN_CULTURES: "cultures",
            BTN_CHEM: "chemicals",
            BTN_FILLERS: "fillers",
        }[text]

        flow[uid] = {"mode": "section", "table": table}
        await update.message.reply_text(text, reply_markup=section_kb())
        return

    if state and state.get("mode") == "section":
        table = state["table"]

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
                else:
                    rs = c.execute(
                        f"SELECT name FROM {table} WHERE active=1 ORDER BY name"
                    ).fetchall()
                    lines = [f"• {r['name']}" for r in rs]

            await update.message.reply_text(
                "📋 СПИСОК\n\n" + ("\n".join(lines) if lines else "Список пуст."),
                reply_markup=section_kb()
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
            if table == "fillers":
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
        reply_markup=active_kb() if job else main_kb()
    )


def main():
    if not TOKEN:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")

    init_db()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle)
    )
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
