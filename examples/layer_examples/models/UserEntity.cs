// @spec RF01
// Example: Invalid Domain Model containing presentation HTML tag
namespace Enterprise.Domain.Models
{
    public class UserEntity
    {
        public int Id { get; set; }
        public string Username { get; set; }
        
        // VIOLATION: ARCH-LAYER-01 (HTML markup inside domain model)
        public string AvatarHtml => "<img src='/avatars/" + Username + ".png' />";
    }
}
