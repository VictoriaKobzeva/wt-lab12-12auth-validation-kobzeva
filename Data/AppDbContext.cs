using Microsoft.EntityFrameworkCore;
using wt_lab12_12auth_validation_kobzeva.Models;

namespace wt_lab12_12auth_validation_kobzeva.Data;

/// <summary>
/// Контекст базы данных приложения.
/// Обеспечивает доступ к таблице Properties через Entity Framework Core.
/// </summary>
public class AppDbContext : DbContext
{
    private readonly string? _schema;

    public AppDbContext(DbContextOptions<AppDbContext> options, IConfiguration configuration)
        : base(options)
    {
        // На Render Free используется одна база PostgreSQL на несколько работ,
        // поэтому приложение может работать в отдельной схеме.
        _schema = configuration["DATABASE_SCHEMA"];
    }

    public DbSet<Property> Properties => Set<Property>();

    public DbSet<User> Users => Set<User>();

    public DbSet<Favorite> Favorites => Set<Favorite>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        if (!string.IsNullOrWhiteSpace(_schema))
        {
            modelBuilder.HasDefaultSchema(_schema);
        }

        modelBuilder.Entity<User>(entity =>
        {
            // Логин должен быть уникальным.
            entity.HasIndex(u => u.Login).IsUnique();

            // Тестовая учётная запись для проверки авторизации.
            // В реальном приложении пароль должен храниться в виде хеша.
            entity.HasData(new User
            {
                Id = 1,
                Login = "student",
                Password = "1234"
            });
        });

        modelBuilder.Entity<Favorite>(entity =>
        {
            // Один пользователь может добавить объект в избранное только один раз.
            entity.HasIndex(f => new { f.UserId, f.PropertyId }).IsUnique();

            entity.HasOne(f => f.User)
                .WithMany()
                .HasForeignKey(f => f.UserId)
                .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(f => f.Property)
                .WithMany()
                .HasForeignKey(f => f.PropertyId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Property>(entity =>
        {
            // Денежные значения хранятся в PostgreSQL как numeric(18, 2).
            entity.Property(p => p.Price).HasPrecision(18, 2);

            // Начальные данные, перенесённые из PropertyStore (WT-5).
            entity.HasData(
                new Property
                {
                    Id = 1,
                    Address = "Тридевятое царство, замок принцессы",
                    Type = "Замок",
                    Price = 999999m,
                    Area = 500,
                    Rooms = 20,
                    IsAvailable = true,
                    Description = "Замок с привидением, рвом и собственным садом"
                },
                new Property
                {
                    Id = 2,
                    Address = "Тёмный лес, избушка на курьих ножках",
                    Type = "Избушка",
                    Price = 666000m,
                    Area = 13,
                    Rooms = 1,
                    IsAvailable = true,
                    Description = "Уютная избушка с печью, рядом остановка ступы"
                },
                new Property
                {
                    Id = 3,
                    Address = "Подводное царство, дворец Нептуна",
                    Type = "Дворец",
                    Price = 5000000m,
                    Area = 1200,
                    Rooms = 50,
                    IsAvailable = false,
                    Description = "Дворец под водой с видом на коралловый риф"
                },
                new Property
                {
                    Id = 4,
                    Address = "Минск, ул. Ленина, 15, кв. 42",
                    Type = "Квартира",
                    Price = 120000m,
                    Area = 65.5,
                    Rooms = 3,
                    IsAvailable = true,
                    Description = "Светлая трёхкомнатная квартира рядом с метро"
                },
                new Property
                {
                    Id = 5,
                    Address = "Минск, пр. Независимости, 100",
                    Type = "Офис",
                    Price = 250000m,
                    Area = 120,
                    Rooms = 5,
                    IsAvailable = true,
                    Description = "Офис в бизнес-центре, есть парковка и охрана"
                },
                new Property
                {
                    Id = 6,
                    Address = "Космос, лунная база Илона Маска",
                    Type = "Космический дом",
                    Price = 1000000000m,
                    Area = 250,
                    Rooms = 5,
                    IsAvailable = true,
                    Description = "Первый жилой дом на Луне, доставка ракетой включена"
                });
        });
    }
}
