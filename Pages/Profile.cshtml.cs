using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.EntityFrameworkCore;
using wt_lab12_12auth_validation_kobzeva.Data;
using wt_lab12_12auth_validation_kobzeva.Models;

namespace wt_lab12_12auth_validation_kobzeva.Pages;

/// <summary>
/// Защищённая страница личного кабинета. Доступна только после входа.
/// Показывает логин пользователя и список избранных объектов недвижимости.
/// </summary>
public class ProfileModel : PageModel
{
    private readonly AppDbContext _context;

    public ProfileModel(AppDbContext context)
    {
        _context = context;
    }

    public string? UserLogin { get; private set; }

    public List<Favorite> Favorites { get; private set; } = new();

    public async Task<IActionResult> OnGetAsync()
    {
        UserLogin = HttpContext.Session.GetString("UserLogin");

        if (UserLogin == null)
        {
            return RedirectToPage("/Login", new { returnUrl = "/Profile" });
        }

        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Login == UserLogin);

        if (user == null)
        {
            HttpContext.Session.Clear();
            return RedirectToPage("/Login");
        }

        Favorites = await _context.Favorites
            .Where(f => f.UserId == user.Id)
            .Include(f => f.Property)
            .OrderByDescending(f => f.AddedAt)
            .ToListAsync();

        return Page();
    }

    public IActionResult OnPost()
    {
        HttpContext.Session.Clear();
        return RedirectToPage("/Login");
    }

    /// <summary>Удаляет объект из избранного текущего пользователя.</summary>
    public async Task<IActionResult> OnPostRemoveFavoriteAsync(int id)
    {
        var login = HttpContext.Session.GetString("UserLogin");

        if (login == null)
        {
            return RedirectToPage("/Login", new { returnUrl = "/Profile" });
        }

        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Login == login);

        if (user != null)
        {
            var favorite = await _context.Favorites
                .FirstOrDefaultAsync(f => f.Id == id && f.UserId == user.Id);

            if (favorite != null)
            {
                _context.Favorites.Remove(favorite);
                await _context.SaveChangesAsync();
            }
        }

        return RedirectToPage("/Profile");
    }
}
