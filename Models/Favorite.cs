using System.ComponentModel.DataAnnotations;

namespace wt_lab12_12auth_validation_kobzeva.Models;

/// <summary>
/// Объект недвижимости, добавленный пользователем в избранное.
/// </summary>
public class Favorite
{
    public int Id { get; set; }

    public int UserId { get; set; }

    public User? User { get; set; }

    public int PropertyId { get; set; }

    public Property? Property { get; set; }

    [Required]
    public DateTime AddedAt { get; set; } = DateTime.UtcNow;
}
