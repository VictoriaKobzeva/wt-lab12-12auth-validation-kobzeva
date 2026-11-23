using System.ComponentModel.DataAnnotations;

namespace wt_lab12_12auth_validation_kobzeva.Models;

/// <summary>
/// Пользователь приложения.
/// В учебных целях пароль хранится в открытом виде; в реальном проекте
/// необходимо использовать хеширование и ASP.NET Core Identity.
/// </summary>
public class User
{
    public int Id { get; set; }

    [Required]
    [StringLength(50)]
    public string Login { get; set; } = "";

    [Required]
    [StringLength(100, MinimumLength = 4)]
    public string Password { get; set; } = "";
}
