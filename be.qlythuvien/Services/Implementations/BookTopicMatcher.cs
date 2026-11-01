using System.Globalization;
using System.Text;
using System.Text.RegularExpressions;

namespace qlthuvien_vip.Services.Implementations;

public static class BookTopicMatcher
{
    private static readonly string[][] Topics =
    {
        new[] { "tai chinh", "dau tu", "quan ly tien", "tiet kiem", "chung khoan", "tien bac", "lam giau" },
        new[] { "kinh te", "kinh doanh", "khoi nghiep", "doanh nghiep" },
        new[] { "thieu nhi", "tre em", "cho be" },
        new[] { "tam ly", "cam xuc", "chua lanh" },
        new[] { "khoa hoc", "vu tru", "vat ly" },
        new[] { "van hoc", "tieu thuyet", "truyen ngan" }
    };
    private static readonly HashSet<string> StopWords = new(
        "toi minh ban cho ve sach cuon quyen tim muon can goi y tu van hay nao co khong mot nhung cac duoi tren gia doc giup voi duoc la va cua nay do nhe di oi hoi".Split(' '));

    public static string Normalize(string? value)
    {
        var decomposed = (value ?? "").ToLowerInvariant().Normalize(NormalizationForm.FormD);
        var plain = new string(decomposed.Where(c => CharUnicodeInfo.GetUnicodeCategory(c) != UnicodeCategory.NonSpacingMark).ToArray()).Replace('đ', 'd');
        return Regex.Replace(Regex.Replace(plain, @"[^a-z0-9]+", " "), @"\s+", " ").Trim();
    }
    private static bool Contains(string text, string phrase) => (" " + text + " ").Contains(" " + phrase + " ");

    public static int Score(string question, string? title, string? author, string? category, string? description)
    {
        var q = Normalize(question);
        var name = Normalize(title);
        var writer = Normalize(author);
        var genre = Normalize(category);
        var details = Normalize(description);
        if (q.Length == 0) return 0;
        if (name.Length > 2 && Contains(q, name)) return 100;
        if (writer.Length > 2 && Contains(q, writer)) return 90;
        var topic = Topics.FirstOrDefault(group => group.Any(term => Contains(q, term)));
        if (topic != null)
        {
            return topic.Max(term => Contains(name, term) ? 80 : Contains(genre, term) ? 70 : Contains(details, term) ? 40 : 0);
        }
        var words = q.Split(' ').Where(w => w.Length > 1 && !StopWords.Contains(w) && !w.Any(char.IsDigit)).Distinct().ToArray();
        if (words.Length == 0) return 0;
        var text = name + " " + writer + " " + genre + " " + details;
        // Require every significant keyword, avoiding matches on generic individual words.
        if (!words.All(w => Contains(text, w))) return 0;
        return words.Sum(w => Contains(name, w) ? 10 : Contains(writer, w) ? 8 : Contains(genre, w) ? 6 : 2);
    }
}
