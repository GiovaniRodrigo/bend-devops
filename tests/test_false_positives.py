"""
==============================================================================
TDD Integration Tests: False Positive Prevention & Real-World Code Scenarios
==============================================================================
@spec RF01, RF02, RF03 - Scanner False Positive Prevention
==============================================================================
"""

import unittest
from pathlib import Path
from scripts.culture_guard import FileAuditResult

class TestFalsePositiveScenarios(unittest.TestCase):
    def test_csharp_domain_model_with_image_methods_not_flagged(self):
        tmp_file = Path("/tmp/CleanImageModel.cs")
        tmp_file.write_text("""// @spec RF01
namespace App.Domain.Models
{
    public class Product
    {
        public int Id { get; set; }
        public string GetImageUrl() => "/products/" + Id + ".png";
        public void SelectCategory(int catId) { }
    }
}
""", encoding="utf-8")
        try:
            audit = FileAuditResult(tmp_file)
            arch_violations = [v for v in audit.violations if v.get("rule_id", "").startswith("ARCH")]
            self.assertEqual(len(arch_violations), 0)
        finally:
            if tmp_file.exists():
                tmp_file.unlink()

    def test_inline_suppression_pragma_exempts_violation_with_reason(self):
        tmp_file = Path("/tmp/SuppressedUserEntity.cs")
        tmp_file.write_text("""// @spec RF01
namespace App.Domain.Models
{
    public class User
    {
        public int Id { get; set; }
        
        // @guardian-ignore ARCH-LAYER-01: Legacy raw avatar markup needed for serializer
        public string AvatarHtml => "<img src='avatar.png' />";
    }
}
""", encoding="utf-8")
        try:
            audit = FileAuditResult(tmp_file)
            arch_violations = [v for v in audit.violations if v.get("rule_id") == "ARCH-LAYER-01"]
            self.assertEqual(len(arch_violations), 0)
        finally:
            if tmp_file.exists():
                tmp_file.unlink()

if __name__ == "__main__":
    unittest.main()
