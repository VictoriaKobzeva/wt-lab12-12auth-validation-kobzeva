#!/usr/bin/env python3
"""Сборка отчёта по лабораторной работе WT-12 в формате DOCX."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "img"
OUT = ROOT / "wt-lab12-kobzeva.docx"

DARK = RGBColor(0x1F, 0x38, 0x64)
MID = RGBColor(0x2E, 0x54, 0x96)
GREY = RGBColor(0x59, 0x59, 0x59)
CODE_BG = "F3F5F8"
HEAD_BG = "DCE6F1"

doc = Document()

# ---------- страница и базовые стили ----------
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin = Cm(2.5)
section.right_margin = Cm(1.5)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.paragraph_format.line_spacing = 1.15
normal.paragraph_format.space_after = Pt(4)

for name, size, color in (("Heading 1", 16, DARK), ("Heading 2", 13, MID)):
    st = doc.styles[name]
    st.font.name = "Times New Roman"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = color
    st.paragraph_format.space_before = Pt(14 if size == 16 else 10)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.keep_with_next = True


def shade(paragraph, fill):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def borders(paragraph, color="D0D7E2"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:space"), "4")
        el.set(qn("w:color"), color)
        pBdr.append(el)
    pPr.append(pBdr)


def code(text, size=8.6):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(2)
    pf.space_after = Pt(8)
    pf.left_indent = Cm(0.25)
    pf.right_indent = Cm(0.1)
    pf.line_spacing = 1.0
    shade(p, CODE_BG)
    borders(p)
    run = p.add_run(text.rstrip())
    run.font.name = "Consolas"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    run.font.size = Pt(size)
    return p


def para(text="", bold=False, italic=False, align=None, size=None, color=None,
         space_after=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if size:
        run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    return p


def bullets(items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        p.add_run(item)


def caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9.5)
    run.font.color.rgb = GREY


def image(name, width=15.4, cap=None):
    path = IMG / name
    if not path.exists():
        para(f"[Скриншот {name} не найден]", italic=True, color=GREY)
        return False
    # Изображение и подпись размещаются в одном абзаце и не разрываются
    # при переходе на новую страницу.
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(10)
    p.paragraph_format.keep_together = True
    p.add_run().add_picture(str(path), width=Cm(width))
    if cap:
        p.add_run().add_break()
        run = p.add_run(cap)
        run.italic = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = GREY
    return True


def table(headers, rows, widths=None, font=10.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(font)
        shade(p, HEAD_BG)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            run = p.add_run(str(value))
            run.font.size = Pt(font)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def add_page_numbers():
    footer = doc.sections[0].footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    run._r.addnext(fld)


# ---------- титульная страница ----------
for _ in range(4):
    doc.add_paragraph()

para("Лабораторная работа WT-12", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
     size=16, color=MID, space_after=12)
para("Авторизация и валидация в Razor Pages\n"
     "с использованием PostgreSQL", bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, size=24, color=DARK, space_after=24)
para("Дисциплина: Web-технологии", align=WD_ALIGN_PARAGRAPH.CENTER,
     size=13, space_after=2)
para("Проект: wt-lab12-12auth-validation-kobzeva", align=WD_ALIGN_PARAGRAPH.CENTER,
     size=13, space_after=2)
para("Выполнила: Кобзева Виктория, группа УИР-1", align=WD_ALIGN_PARAGRAPH.CENTER,
     size=13, space_after=2)
para("Дата: 23.11.2026", align=WD_ALIGN_PARAGRAPH.CENTER, size=13, space_after=2)

for _ in range(6):
    doc.add_paragraph()

para("GitHub:", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
para("https://github.com/VictoriaKobzeva/wt-lab12-12auth-validation-kobzeva",
     align=WD_ALIGN_PARAGRAPH.CENTER, size=11, color=MID)
doc.add_page_break()

# ---------- цель ----------
doc.add_heading("1. Цель работы", level=1)
para("Изучить основные принципы авторизации и валидации данных в приложении "
     "ASP.NET Core Razor Pages с использованием PostgreSQL и Entity Framework Core.")
para("В ходе работы необходимо было:")
bullets([
    "добавить в приложение сущность пользователя;",
    "сохранить пользователей в PostgreSQL;",
    "реализовать форму входа;",
    "реализовать выход пользователя;",
    "ограничить доступ к отдельной странице;",
    "реализовать проверку введённых данных;",
    "использовать атрибуты валидации модели;",
    "проверить работу авторизации и валидации.",
])

# ---------- исходное приложение ----------
doc.add_heading("2. Исходное приложение и предметная область", level=1)
para("За основу взято приложение из лабораторной работы WT-8 "
     "(wt-lab8-8razor-postgresql-kobzeva), подключённое к PostgreSQL через "
     "Entity Framework Core. Создана его копия wt-lab12-12auth-validation-kobzeva. "
     "Структура страниц, маршруты и предметная область сохранены.")
para("Предметная область — агентство недвижимости. Основная сущность — Property, "
     "таблица — Properties. В приложении уже реализованы CRUD-операции и поиск "
     "по адресу, типу и описанию. В WT-12 к существующему приложению добавлены "
     "пользователи, авторизация, защищённая страница и серверная валидация.")
para("В шаблоне методических указаний используется сущность Product и таблица "
     "Products. В проекте сохранена предметная область лабораторных работ "
     "№ 5–8, поэтому сущность называется Property, а таблица — Properties. "
     "Набор операций и структура базы данных полностью соответствуют заданию.")

# ---------- архитектура ----------
doc.add_heading("3. Архитектура приложения", level=1)
code("""Браузер
   │
   ├── Страница входа (/Login)
   ├── Страницы недвижимости (/Products)
   └── Защищённая страница (/Profile)
   │
   ▼
Razor Pages
   │
   ├── Авторизация (Session)
   ├── Валидация (DataAnnotations, ModelState)
   └── Model Binding
   │
   ▼
Entity Framework Core
   │
   ▼
PostgreSQL""")
para("Авторизация и работа с данными — разные задачи. Авторизация определяет, "
     "вошёл ли пользователь в систему, валидация проверяет корректность "
     "введённых данных, а EF Core обеспечивает работу приложения с PostgreSQL.")

# ---------- модель пользователя ----------
doc.add_heading("4. Модель пользователя User", level=1)
para("Создан файл Models/User.cs:")
code("""using System.ComponentModel.DataAnnotations;

namespace wt_lab12_12auth_validation_kobzeva.Models;

public class User
{
    public int Id { get; set; }

    [Required]
    [StringLength(50)]
    public string Login { get; set; } = "";

    [Required]
    [StringLength(100, MinimumLength = 4)]
    public string Password { get; set; } = "";
}""")
para("В учебных целях пароль хранится в базе данных в открытом виде. "
     "В реальном приложении необходимо использовать безопасное хеширование "
     "паролей и специализированные механизмы ASP.NET Core Identity.")

# ---------- AppDbContext ----------
doc.add_heading("5. Добавление таблицы пользователей в Entity Framework Core", level=1)
para("В Data/AppDbContext.cs добавлено свойство DbSet<User> и конфигурация "
     "уникального индекса по логину. Тестовая учётная запись добавляется "
     "начальными данными (HasData), поэтому она создаётся вместе с миграцией:")
code("""public DbSet<Property> Properties => Set<Property>();

public DbSet<User> Users => Set<User>();

protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    base.OnModelCreating(modelBuilder);

    modelBuilder.Entity<User>(entity =>
    {
        // Логин должен быть уникальным.
        entity.HasIndex(u => u.Login).IsUnique();

        // Тестовая учётная запись для проверки авторизации.
        entity.HasData(new User
        {
            Id = 1,
            Login = "student",
            Password = "1234"
        });
    });
}""")
para("DbSet<User> Users представляет набор пользователей, с которым выполняются "
     "запросы при входе в систему. Уникальный индекс не позволяет создать двух "
     "пользователей с одинаковым логином.")

# ---------- миграция ----------
doc.add_heading("6. Создание миграции AddUsers", level=1)
para("Миграция создана и применена командами:")
code("""dotnet ef migrations add AddUsers
dotnet ef database update""")
para("Сгенерированная миграция создаёт таблицу Users, добавляет тестового "
     "пользователя и уникальный индекс по логину:")
code("""migrationBuilder.CreateTable(
    name: "Users",
    columns: table => new
    {
        Id = table.Column<int>(type: "integer", nullable: false)
            .Annotation("Npgsql:ValueGenerationStrategy",
                NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
        Login = table.Column<string>(type: "character varying(50)",
            maxLength: 50, nullable: false),
        Password = table.Column<string>(type: "character varying(100)",
            maxLength: 100, nullable: false)
    },
    constraints: table =>
    {
        table.PrimaryKey("PK_Users", x => x.Id);
    });

migrationBuilder.InsertData(
    table: "Users",
    columns: new[] { "Id", "Login", "Password" },
    values: new object[] { 1, "student", "1234" });

migrationBuilder.CreateIndex(
    name: "IX_Users_Login",
    table: "Users",
    column: "Login",
    unique: true);""")
para("При запуске приложение автоматически применяет неприменённые миграции:")
code("""using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}""")

# ---------- таблица Users ----------
doc.add_heading("7. Таблица Users в PostgreSQL", level=1)
para("После применения миграции в базе wt_lab12 появилась таблица Users. "
     "Структура таблицы и содержимое проверены в pgAdmin 4:")
image("11-users-table.png", 16.4,
      "Рис. 1. Таблица Users в PostgreSQL (pgAdmin 4)")
para("В таблице присутствуют поля Id (первичный ключ), Login и Password. "
     "Запрос SELECT * FROM \"Users\" возвращает тестовую учётную запись:")
table(["Id", "Login", "Password"],
      [["1", "student", "1234"]],
      widths=[3.0, 6.0, 6.0])
para("Пароль хранится в открытом виде только в учебных целях. Для промышленной "
     "реализации используется ASP.NET Core Identity с хешированием паролей.")

# ---------- страница входа ----------
doc.add_heading("8. Страница авторизации", level=1)
para("Создана страница Pages/Login.cshtml с формой входа, сообщениями валидации "
     "и поддержкой возврата на запрошенную страницу:")
code("""@page
@model LoginModel

@{ ViewData["Title"] = "Вход"; }

@if (!string.IsNullOrWhiteSpace(Model.ReturnUrl))
{
    <div class="alert alert-warning">
        Для доступа к личному кабинету необходимо войти в систему.
    </div>
}

<div asp-validation-summary="ModelOnly" class="text-danger"></div>

<form method="post">
    <label asp-for="Login">Логин</label>
    <input asp-for="Login" autocomplete="username" />
    <span asp-validation-for="Login" class="text-danger"></span>

    <label asp-for="Password">Пароль</label>
    <input asp-for="Password" type="password"
           autocomplete="current-password" />
    <span asp-validation-for="Password" class="text-danger"></span>

    <button type="submit">Войти</button>
</form>""")
para("Страница входа в браузере:")
image("01-login.png", 11.4, "Рис. 2. Страница входа /Login")

# ---------- модель страницы Login ----------
doc.add_heading("9. Реализация модели страницы Login", level=1)
para("В Pages/Login.cshtml.cs реализованы серверная валидация, проверка логина и "
     "пароля в PostgreSQL и сохранение логина в Session:")
code("""public class LoginModel : PageModel
{
    private readonly AppDbContext _context;

    public LoginModel(AppDbContext context)
    {
        _context = context;
    }

    [BindProperty]
    [Required(ErrorMessage = "Введите логин")]
    [StringLength(50, MinimumLength = 3,
        ErrorMessage = "Логин должен содержать от 3 до 50 символов")]
    public string Login { get; set; } = "";

    [BindProperty]
    [Required(ErrorMessage = "Введите пароль")]
    [StringLength(100, MinimumLength = 4,
        ErrorMessage = "Пароль должен содержать не менее 4 символов")]
    public string Password { get; set; } = "";

    [BindProperty(SupportsGet = true)]
    public string? ReturnUrl { get; set; }

    public async Task<IActionResult> OnPostAsync()
    {
        // Серверная валидация выполняется до обращения к базе данных.
        if (!ModelState.IsValid)
        {
            return Page();
        }

        var user = await _context.Users
            .FirstOrDefaultAsync(
                x => x.Login == Login && x.Password == Password);

        if (user == null)
        {
            ModelState.AddModelError("", "Неверный логин или пароль.");
            return Page();
        }

        HttpContext.Session.SetString("UserLogin", user.Login);

        if (!string.IsNullOrWhiteSpace(ReturnUrl) && Url.IsLocalUrl(ReturnUrl))
        {
            return LocalRedirect(ReturnUrl);
        }

        return RedirectToPage("/Profile");
    }
}""")
para("Атрибуты [Required] и [StringLength] задают правила валидации, а "
     "ModelState.IsValid проверяет их до выполнения запроса к PostgreSQL. "
     "Метод FirstOrDefaultAsync() ищет пользователя с указанными логином и "
     "паролем; если пользователь не найден, выводится сообщение об ошибке.")

# ---------- Session ----------
doc.add_heading("10. Подключение Session", level=1)
para("В Program.cs зарегистрированы Session и middleware:")
code("""builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

// ...

app.UseRouting();

app.UseSession();

app.UseAuthorization();

app.MapRazorPages();""")
para("Session хранит значение UserLogin и позволяет определить, что пользователь "
     "выполнил вход. Время жизни сессии — 30 минут.")

# ---------- Profile ----------
doc.add_heading("11. Защищённая страница Profile", level=1)
para("Создана страница Pages/Profile.cshtml, доступная только авторизованным "
     "пользователям:")
code("""@page
@model ProfileModel

@{ ViewData["Title"] = "Личный кабинет"; }

<h1>Личный кабинет</h1>
<p>Пользователь: <strong>@Model.UserLogin</strong></p>

<form method="post">
    <button type="submit">Выйти</button>
</form>""")
para("Модель страницы проверяет наличие логина в Session и очищает Session при "
     "выходе:")
code("""public class ProfileModel : PageModel
{
    public string? UserLogin { get; private set; }

    public IActionResult OnGet()
    {
        UserLogin = HttpContext.Session.GetString("UserLogin");

        if (UserLogin == null)
        {
            return RedirectToPage("/Login", new { returnUrl = "/Profile" });
        }

        return Page();
    }

    public IActionResult OnPost()
    {
        HttpContext.Session.Clear();
        return RedirectToPage("/Login");
    }
}""")
para("При обращении к /Profile без авторизации пользователь перенаправляется на "
     "страницу входа с параметром returnUrl. После успешного входа приложение "
     "возвращает его на /Profile.")

# ---------- навигация ----------
doc.add_heading("12. Добавление навигации", level=1)
para("В Pages/Shared/_Layout.cshtml добавлены ссылки на страницы входа и личного "
     "кабинета, а также отображение текущего пользователя:")
code("""@{
    var currentUser = Context.Session.GetString("UserLogin");
}

<a asp-page="/Index">Главная</a>
<a asp-page="/Products/Index">Недвижимость</a>
<a asp-page="/Profile">Личный кабинет</a>

@if (currentUser == null)
{
    <a asp-page="/Login">Войти</a>
}
else
{
    <span>Вы вошли как <strong>@currentUser</strong></span>
}""")

# ---------- проверка работы ----------
doc.add_heading("13. Проверка работы приложения", level=1)
para("Приложение запущено командой dotnet run и проверено по сценариям "
     "методических указаний.")

doc.add_heading("13.1. Сценарий 1. Пустая форма", level=2)
para("На странице /Login нажата кнопка «Войти» без ввода данных. Появились "
     "сообщения «Введите логин» и «Введите пароль»:")
image("02-validation-empty.png", 11.4,
      "Рис. 3. Сообщения валидации для пустой формы")

doc.add_heading("13.2. Сценарий 2. Слишком короткий логин", level=2)
para("Введён логин ab. Появилось сообщение «Логин должен содержать от 3 до 50 "
     "символов»:")
image("03-validation-short-login.png", 11.4,
      "Рис. 4. Валидация слишком короткого логина")

doc.add_heading("13.3. Сценарий 3. Слишком короткий пароль", level=2)
para("Введён пароль 123. Появилось сообщение «Пароль должен содержать не менее "
     "4 символов»:")
image("04-validation-short-password.png", 11.4,
      "Рис. 5. Валидация слишком короткого пароля")

doc.add_heading("13.4. Сценарий 4. Неверные учётные данные", level=2)
para("Введены логин student и пароль 9999. Появилось сообщение «Неверный логин "
     "или пароль.»:")
image("05-wrong-credentials.png", 11.4,
      "Рис. 6. Сообщение при неверных учётных данных")

doc.add_heading("13.5. Сценарий 5. Успешная авторизация", level=2)
para("Введены логин student и пароль 1234. Приложение перенаправило пользователя "
     "на страницу /Profile, где отображается логин и приветственное сообщение:")
image("06-login-success.png", 11.4,
      "Рис. 7. Результат успешного входа — страница /Profile")

doc.add_heading("13.6. Сценарий 6. Выход", level=2)
para("Нажата кнопка «Выйти». Session очищена, выполнен переход на страницу "
     "входа:")
image("07-logout.png", 11.4,
      "Рис. 8. Результат выхода — страница /Login")

doc.add_heading("13.7. Сценарий 7. Доступ к /Profile без авторизации", level=2)
para("После выхода выполнен прямой переход на /Profile. Приложение "
     "перенаправило на /Login и показало предупреждение о необходимости входа:")
image("08-profile-unauthorized.png", 11.4,
      "Рис. 9. Перенаправление на /Login при попытке открыть /Profile")

doc.add_heading("13.8. Работающее приложение", level=2)
para("Каталог недвижимости и главная страница приложения продолжают работать и "
     "используют данные из PostgreSQL:")
image("09-products.png", 10.2,
      "Рис. 10. Каталог недвижимости (/Products)")
image("10-home.png", 11.4,
      "Рис. 11. Главная страница приложения")

# ---------- итоговая структура ----------
doc.add_heading("14. Итоговая структура проекта", level=1)
code("""wt-lab12-12auth-validation-kobzeva/
│
├── Data/
│   └── AppDbContext.cs
│
├── Models/
│   ├── Property.cs
│   └── User.cs
│
├── Migrations/
│   ├── 20261119115243_InitialCreate.cs
│   ├── 20261119115322_AddPropertyDescription.cs
│   ├── 20261122145924_AddUsers.cs
│   └── AppDbContextModelSnapshot.cs
│
├── Pages/
│   ├── Products/
│   │   ├── Index.cshtml(.cs)
│   │   ├── Create.cshtml(.cs)
│   │   ├── Edit.cshtml(.cs)
│   │   └── Details.cshtml(.cs)
│   ├── Shared/
│   │   └── _Layout.cshtml
│   ├── Login.cshtml(.cs)
│   ├── Profile.cshtml(.cs)
│   └── Index.cshtml(.cs)
│
├── wwwroot/
├── docs/
│   ├── build_report.py
│   └── img/
├── appsettings.json
├── appsettings.Development.json
├── Program.cs
├── Dockerfile
├── render.yaml
└── wt-lab12-12auth-validation-kobzeva.csproj""")

# ---------- GitHub ----------
doc.add_heading("15. GitHub-репозиторий", level=1)
para("Проект опубликован в GitHub:")
para("https://github.com/VictoriaKobzeva/wt-lab12-12auth-validation-kobzeva",
     bold=True, color=MID)
para("В репозитории размещены исходный код, модель User, AppDbContext, миграции, "
     "страницы Login и Profile, Dockerfile, render.yaml, README и отчёт. Файл "
     "appsettings.Development.json с локальным паролем добавлен в .gitignore и "
     "в GitHub не попадает.")

# ---------- результаты ----------
doc.add_heading("16. Результаты проверки работоспособности", level=1)
table(["Проверка", "Где проверено", "Результат"],
      [["Таблица Users", "pgAdmin 4", "Поля Id, Login, Password; пользователь student"],
       ["Пустая форма", "/Login", "«Введите логин», «Введите пароль»"],
       ["Короткий логин", "/Login (ab)", "«Логин должен содержать от 3 до 50 символов»"],
       ["Короткий пароль", "/Login (123)", "«Пароль должен содержать не менее 4 символов»"],
       ["Неверные данные", "student / 9999", "«Неверный логин или пароль.»"],
       ["Успешный вход", "student / 1234", "Переход на /Profile, логин отображается"],
       ["Выход", "Кнопка «Выйти»", "Переход на /Login, Session очищена"],
       ["/Profile без входа", "Прямой переход", "Перенаправление на /Login"],
       ["Каталог недвижимости", "/Products", "6 объектов из PostgreSQL"],
       ["Главная страница", "/", "200 OK"]],
      widths=[4.6, 4.8, 6.4], font=10)

# ---------- вывод ----------
doc.add_heading("17. Вывод", level=1)
para("В ходе работы в приложение Razor Pages добавлена авторизация на основе "
     "Session. Создана модель User, таблица Users в PostgreSQL и миграция "
     "AddUsers с тестовой учётной записью. Реализованы страница входа, проверка "
     "логина и пароля по базе данных, защищённая страница личного кабинета и "
     "выход пользователя.")
para("Форма входа защищена серверной валидацией: атрибуты [Required] и "
     "[StringLength] и проверка ModelState.IsValid не позволяют обратиться к "
     "базе данных при некорректном вводе. Проверены все сценарии методических "
     "указаний: пустая форма, короткие логин и пароль, неверные данные, успешный "
     "вход, выход и отказ в доступе к /Profile без авторизации.")
para("Приложение опубликовано в GitHub. Пароль в учебном проекте хранится в "
     "открытом виде; в реальной системе необходимо использовать хеширование и "
     "ASP.NET Core Identity.")

# ---------- приложение ----------
doc.add_page_break()
doc.add_heading("Приложение А. Контрольные вопросы", level=1)
qa = [
    ("Что такое авторизация?",
     "Процесс определения прав пользователя на выполнение действий и доступ "
     "к ресурсам после установления его личности."),
    ("Чем авторизация отличается от аутентификации?",
     "Аутентификация проверяет, кто пользователь (логин и пароль), а "
     "авторизация определяет, что ему разрешено делать."),
    ("Для чего используется Session?",
     "Для хранения данных о пользователе между HTTP-запросами на сервере."),
    ("Что хранится в Session в данной работе?",
     "Логин пользователя в значении UserLogin после успешного входа."),
    ("Что происходит после успешного входа?",
     "Логин записывается в Session, пользователь перенаправляется на /Profile "
     "или на returnUrl."),
    ("Для чего используется HttpContext.Session?",
     "Для чтения, записи и очистки данных текущей сессии."),
    ("Для чего используется [BindProperty]?",
     "Для автоматической привязки данных формы к свойствам PageModel."),
    ("Что такое Model Binding?",
     "Механизм сопоставления данных HTTP-запроса (формы, query, route) "
     "свойствам модели."),
    ("Для чего используется [Required]?",
     "Указывает, что значение обязательно должно быть заполнено."),
    ("Для чего используется [StringLength]?",
     "Ограничивает максимальную и минимальную длину строки."),
    ("Что такое ModelState?",
     "Набор значений и ошибок валидации, полученных при привязке модели."),
    ("Для чего используется ModelState.IsValid?",
     "Проверяет, что при привязке модели не возникло ошибок валидации."),
    ("Почему валидацию необходимо выполнять до обращения к базе данных?",
     "Чтобы не выполнять лишние запросы и не обрабатывать заведомо "
     "некорректные данные."),
    ("Для чего используется FirstOrDefaultAsync()?",
     "Асинхронно возвращает первый подходящий элемент или null, если его нет."),
    ("Как приложение определяет, существует ли пользователь?",
     "Запросом к таблице Users по логину и паролю; если результат null, "
     "пользователь не найден."),
    ("Что происходит при неправильном логине или пароле?",
     "В ModelState добавляется ошибка «Неверный логин или пароль.», страница "
     "отображается снова."),
    ("Как ограничивается доступ к странице Profile?",
     "В OnGet() проверяется наличие логина в Session; при его отсутствии "
     "выполняется перенаправление на /Login."),
    ("Что происходит после выхода пользователя?",
     "Session очищается, пользователь перенаправляется на /Login."),
    ("Для чего используется RedirectToPage()?",
     "Для перенаправления на другую Razor-страницу по её имени."),
    ("Почему хранение открытого пароля допустимо только в учебном примере?",
     "При утечке базы пароли станут известны; в реальных системах пароли "
     "хранят только в виде хеша."),
    ("Какой механизм ASP.NET Core используется для промышленной реализации "
     "учётных записей?",
     "ASP.NET Core Identity."),
    ("Где находятся данные пользователей после выполнения миграции?",
     "В таблице Users базы данных PostgreSQL."),
    ("Что делает команда dotnet ef migrations add?",
     "Создаёт миграцию на основе изменений модели."),
    ("Что делает команда dotnet ef database update?",
     "Применяет неприменённые миграции к базе данных."),
    ("Как связаны Razor Pages, EF Core и PostgreSQL?",
     "PageModel через AppDbContext и EF Core обращается к PostgreSQL, получая "
     "и сохраняя данные."),
]
table(["Вопрос", "Ответ"], qa, widths=[6.2, 9.6], font=9.5)

add_page_numbers()
doc.core_properties.title = "Лабораторная работа WT-12"
doc.core_properties.author = "Кобзева Виктория"
doc.core_properties.subject = "Авторизация и валидация в Razor Pages с PostgreSQL"

doc.save(OUT)
print(f"Сохранено: {OUT}")
