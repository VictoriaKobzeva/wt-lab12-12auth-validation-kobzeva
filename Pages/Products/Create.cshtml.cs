using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using wt_lab12_12auth_validation_kobzeva.Data;
using wt_lab12_12auth_validation_kobzeva.Models;

namespace wt_lab12_12auth_validation_kobzeva.Pages.Products;

public class CreateModel : PageModel
{
    private readonly AppDbContext _context;

    public CreateModel(AppDbContext context)
    {
        _context = context;
    }

    [BindProperty]
    public Property Property { get; set; } = new();

    public void OnGet()
    {
        // GET: показать пустую форму
    }

    public async Task<IActionResult> OnPostAsync()
    {
        if (!ModelState.IsValid)
        {
            return Page();
        }

        _context.Properties.Add(Property);
        await _context.SaveChangesAsync();

        return RedirectToPage("./Index");
    }
}
