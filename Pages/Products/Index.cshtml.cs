using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.EntityFrameworkCore;
using wt_lab12_12auth_validation_kobzeva.Data;
using wt_lab12_12auth_validation_kobzeva.Models;

namespace wt_lab12_12auth_validation_kobzeva.Pages.Products;

public class IndexModel : PageModel
{
    private readonly AppDbContext _context;

    public IndexModel(AppDbContext context)
    {
        _context = context;
    }

    public List<Property> Properties { get; set; } = new();

    /// <summary>Идентификаторы объектов, которые текущий пользователь добавил в избранное.</summary>
    public HashSet<int> FavoriteIds { get; set; } = new();

    public string? CurrentUserLogin { get; private set; }

    /// <summary>Текущий адрес каталога — используется для возврата после входа.</summary>
    public string CurrentUrl => $"{Request.Path}{Request.QueryString}";

    [BindProperty(SupportsGet = true)]
    public string? Search { get; set; }

    public async Task OnGetAsync()
    {
        var query = _context.Properties.AsQueryable();

        if (!string.IsNullOrWhiteSpace(Search))
        {
            var pattern = $"%{Search.Trim()}%";
            query = query.Where(p =>
                EF.Functions.ILike(p.Address, pattern) ||
                EF.Functions.ILike(p.Type, pattern) ||
                EF.Functions.ILike(p.Description, pattern));
        }

        Properties = await query
            .OrderBy(p => p.Address)
            .ToListAsync();

        CurrentUserLogin = HttpContext.Session.GetString("UserLogin");

        if (!string.IsNullOrWhiteSpace(CurrentUserLogin))
        {
            var userId = await _context.Users
                .Where(u => u.Login == CurrentUserLogin)
                .Select(u => (int?)u.Id)
                .FirstOrDefaultAsync();

            if (userId != null)
            {
                FavoriteIds = (await _context.Favorites
                        .Where(f => f.UserId == userId.Value)
                        .Select(f => f.PropertyId)
                        .ToListAsync())
                    .ToHashSet();
            }
        }
    }

    public async Task<IActionResult> OnPostDeleteAsync(int id)
    {
        var property = await _context.Properties.FindAsync(id);

        if (property != null)
        {
            _context.Properties.Remove(property);
            await _context.SaveChangesAsync();
        }

        return RedirectToPage("./Index");
    }

    /// <summary>Добавляет объект в избранное или убирает его оттуда.</summary>
    public async Task<IActionResult> OnPostToggleFavoriteAsync(int id, string? returnUrl)
    {
        var login = HttpContext.Session.GetString("UserLogin");

        // Неавторизованного пользователя отправляем на вход и запоминаем,
        // куда вернуться после успешной авторизации.
        if (string.IsNullOrWhiteSpace(login))
        {
            var target = string.IsNullOrWhiteSpace(returnUrl) ? "/Products" : returnUrl;
            return RedirectToPage("/Login", new { returnUrl = target });
        }

        var user = await _context.Users.FirstOrDefaultAsync(u => u.Login == login);
        var propertyExists = await _context.Properties.AnyAsync(p => p.Id == id);

        if (user == null || !propertyExists)
        {
            return RedirectToPage("./Index");
        }

        var favorite = await _context.Favorites
            .FirstOrDefaultAsync(f => f.UserId == user.Id && f.PropertyId == id);

        if (favorite == null)
        {
            _context.Favorites.Add(new Favorite
            {
                UserId = user.Id,
                PropertyId = id,
                AddedAt = DateTime.UtcNow
            });
        }
        else
        {
            _context.Favorites.Remove(favorite);
        }

        await _context.SaveChangesAsync();

        if (!string.IsNullOrWhiteSpace(returnUrl) && Url.IsLocalUrl(returnUrl))
        {
            return LocalRedirect(returnUrl);
        }

        return RedirectToPage("./Index");
    }
}
