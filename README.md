# Лабораторная работа № 12. Авторизация и валидация в Razor Pages с использованием PostgreSQL

Проект: **wt-lab12-12auth-validation-kobzeva**

Приложение ASP.NET Core Razor Pages для учёта недвижимости. Данные хранятся в
PostgreSQL, доступ выполняется через Entity Framework Core (Code First, миграции).
В работе добавлены авторизация на основе Session, защищённая страница личного
кабинета и серверная валидация формы входа.

- **GitHub:** <https://github.com/VictoriaKobzeva/wt-lab12-12auth-validation-kobzeva>
- **Отчёт:** `wt-lab12-kobzeva.pdf` (исходник — `docs/build_report.py`)
- **Локальная БД:** PostgreSQL 16, `localhost:5432`, база `wt_lab12`, пользователь `postgres`
- **Публикация:** подготовлен `render.yaml` (Render, Docker)

## Предметная область

Агентство недвижимости. Основная сущность — `Property`:

| Свойство | Тип | Назначение |
|---|---|---|
| `Id` | `int` | Идентификатор |
| `Address` | `string` | Адрес объекта |
| `Type` | `string` | Тип: квартира, дом, офис, замок |
| `Price` | `decimal(18,2)` | Цена |
| `Area` | `double` | Площадь, м² |
| `Rooms` | `int` | Количество комнат |
| `IsAvailable` | `bool` | Доступность |
| `Description` | `string(1000)` | Описание (добавлено миграцией) |

> В шаблоне лабораторной работы используется сущность `Product` и таблица
> `Products`. В проекте сохранена предметная область лабораторных работ № 5–8,
> поэтому сущность называется `Property`, а таблица — `Properties`.

## Что добавлено в WT-12

| Элемент | Файл |
|---|---|
| Модель пользователя | `Models/User.cs` |
| Таблица `Users` | `Data/AppDbContext.cs`, миграция `AddUsers` |
| Страница входа | `Pages/Login.cshtml`, `Pages/Login.cshtml.cs` |
| Защищённая страница | `Pages/Profile.cshtml`, `Pages/Profile.cshtml.cs` |
| Session | `Program.cs` (`AddSession`, `UseSession`) |
| Навигация | `Pages/Shared/_Layout.cshtml` |

Тестовая учётная запись: **student / 1234**. Она добавляется миграцией
`AddUsers` (`HasData`), поэтому после `dotnet ef database update` пользователь
уже есть в таблице `Users`.

## Архитектура

```text
Браузер
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
PostgreSQL
```

Авторизация и валидация — разные задачи: авторизация определяет, вошёл ли
пользователь в систему, а валидация проверяет корректность введённых данных до
обращения к базе.

## Структура проекта

```text
wt-lab12-12auth-validation-kobzeva/
├── Data/
│   └── AppDbContext.cs
├── Models/
│   ├── Property.cs
│   └── User.cs
├── Migrations/
│   ├── 20261119115243_InitialCreate.cs
│   ├── 20261119115322_AddPropertyDescription.cs
│   ├── 20261122145924_AddUsers.cs
│   └── AppDbContextModelSnapshot.cs
├── Pages/
│   ├── Products/
│   │   ├── Index.cshtml(.cs)      — список, поиск, удаление
│   │   ├── Create.cshtml(.cs)     — создание
│   │   ├── Edit.cshtml(.cs)       — редактирование
│   │   └── Details.cshtml(.cs)    — просмотр
│   ├── Login.cshtml(.cs)          — вход, валидация
│   ├── Profile.cshtml(.cs)        — защищённая страница, выход
│   ├── Index.cshtml(.cs)
│   └── Shared/_Layout.cshtml
├── wwwroot/
├── docs/
│   ├── build_report.py            — сборка отчёта
│   └── img/                       — скриншоты для отчёта
├── Program.cs
├── appsettings.json
├── appsettings.Development.json
├── Dockerfile
├── render.yaml
└── wt-lab12-12auth-validation-kobzeva.csproj
```

## Локальный запуск

1. Создать базу данных PostgreSQL:

```bash
createdb -h localhost -p 5432 -U postgres wt_lab12
```

2. Указать строку подключения в `appsettings.Development.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=wt_lab12;Username=postgres;Password=your_password"
  }
}
```

Файл добавлен в `.gitignore`, реальный пароль в репозиторий не попадает.

3. Применить миграции и запустить приложение:

```bash
dotnet restore
dotnet ef database update
dotnet run
```

Приложение слушает порт из переменной `PORT` (по умолчанию `10000`):
<http://localhost:10000/Login>.

При старте приложение автоматически применяет неприменённые миграции
(`db.Database.Migrate()`), поэтому `database update` можно не выполнять отдельно.

## Авторизация

Вход выполняется на странице `/Login`. После успешной проверки логина и пароля
в Session записывается значение `UserLogin`:

```csharp
HttpContext.Session.SetString("UserLogin", user.Login);
```

Session настраивается в `Program.cs`:

```csharp
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
});

app.UseSession();
```

Защищённая страница `/Profile` проверяет наличие значения в Session и при его
отсутствии перенаправляет на страницу входа:

```csharp
UserLogin = HttpContext.Session.GetString("UserLogin");

if (UserLogin == null)
{
    return RedirectToPage("/Login", new { returnUrl = "/Profile" });
}
```

После входа приложение возвращает пользователя на запрошенную страницу через
безопасный `LocalRedirect(returnUrl)`. Выход очищает Session:

```csharp
public IActionResult OnPost()
{
    HttpContext.Session.Clear();
    return RedirectToPage("/Login");
}
```

## Валидация

Валидация выполняется на сервере до запроса к PostgreSQL. Атрибуты модели
`LoginModel`:

```csharp
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
```

Проверка `ModelState` стоит первой строкой `OnPostAsync()`:

```csharp
public async Task<IActionResult> OnPostAsync()
{
    if (!ModelState.IsValid)
    {
        return Page();
    }

    var user = await _context.Users
        .FirstOrDefaultAsync(x => x.Login == Login && x.Password == Password);

    if (user == null)
    {
        ModelState.AddModelError("", "Неверный логин или пароль.");
        return Page();
    }

    HttpContext.Session.SetString("UserLogin", user.Login);
    // ...
}
```

Проверяемые сценарии:

| Сценарий | Ввод | Сообщение / результат |
|---|---|---|
| 1. Пустая форма | — | «Введите логин», «Введите пароль» |
| 2. Короткий логин | `ab` | «Логин должен содержать от 3 до 50 символов» |
| 3. Короткий пароль | `123` | «Пароль должен содержать не менее 4 символов» |
| 4. Неверные данные | `student` / `9999` | «Неверный логин или пароль.» |
| 5. Успешный вход | `student` / `1234` | Переход на `/Profile` |
| 6. Выход | кнопка «Выйти» | Переход на `/Login` |
| 7. `/Profile` без входа | прямой переход | Перенаправление на `/Login` |

## Миграции

```bash
dotnet ef migrations add <Name>
dotnet ef database update
dotnet ef migrations list
```

| Миграция | Назначение |
|---|---|
| `20261119115243_InitialCreate` | Таблицы `Properties` и `__EFMigrationsHistory`, начальные данные |
| `20261119115322_AddPropertyDescription` | Столбец `Description` (`varchar(1000)`) |
| `20261122145924_AddUsers` | Таблица `Users`, уникальный индекс `IX_Users_Login`, тестовый пользователь `student` |

## Таблица Users

```sql
SELECT * FROM "Users";
```

| Id | Login | Password |
|---|---|---|
| 1 | student | 1234 |

> Пароль хранится в открытом виде только в учебных целях. В реальном проекте
> используется хеширование и ASP.NET Core Identity.

## Docker

```bash
docker build -t wt-lab12-12auth-validation-kobzeva .
docker run -p 10000:10000 \
  -e DATABASE_URL="postgres://user:password@host:5432/wt_lab12" \
  wt-lab12-12auth-validation-kobzeva
```

Проверка: <http://localhost:10000/Login>

## Render

`Program.cs` поддерживает два источника строки подключения:

- локально — `ConnectionStrings:DefaultConnection`;
- на Render — переменная окружения `DATABASE_URL` (Internal Database URL),
  которая преобразуется в строку подключения Npgsql.

Порт берётся из переменной `PORT` (по умолчанию `10000`), приложение слушает
`http://0.0.0.0:{port}`. Миграции применяются при запуске контейнера.

### Отдельная схема на Render

Бесплатный тариф Render допускает только один активный инстанс PostgreSQL на
аккаунт, поэтому лабораторная работа использует существующий инстанс, но
работает в отдельной схеме `wt_lab12`. Схема задаётся переменной окружения
`DATABASE_SCHEMA`; в строку подключения добавляется `Search Path=wt_lab12`, а
таблицы `Properties`, `Users` и `__EFMigrationsHistory` создаются внутри этой
схемы. Данные других лабораторных работ не затрагиваются.

```csharp
var databaseSchema = builder.Configuration["DATABASE_SCHEMA"];
connectionString += $";Search Path={databaseSchema}";
```

В каталоге есть `render.yaml` — вариант развёртывания через Blueprint: он создаёт
PostgreSQL и Web Service (Runtime: Docker) и связывает их через `DATABASE_URL`.
В рамках WT-12 развёртывание на Render не выполнялось: конфигурация подготовлена,
приложение проверено локально.

## Ссылки

- GitHub-репозиторий: <https://github.com/VictoriaKobzeva/wt-lab12-12auth-validation-kobzeva>
- Отчёт: `wt-lab12-kobzeva.pdf`
