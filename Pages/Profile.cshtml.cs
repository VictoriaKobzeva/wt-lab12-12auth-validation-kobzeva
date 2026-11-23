using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace wt_lab12_12auth_validation_kobzeva.Pages;

/// <summary>
/// Защищённая страница личного кабинета. Доступна только после входа.
/// </summary>
public class ProfileModel : PageModel
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
}
