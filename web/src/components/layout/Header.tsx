import { Menu, Globe, Sun, Moon } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { useTheme } from "@/hooks/useTheme";

const navItems = [
  { key: "header.about", href: "#about" },
  { key: "header.experience", href: "#experience" },
  { key: "header.projects", href: "#projects" },
  { key: "header.skills", href: "#skills" },
  { key: "header.contact", href: "#contact" },
];

export function Header() {
  const [open, setOpen] = useState(false);
  const { i18n, t } = useTranslation();
  const { theme, toggleTheme } = useTheme();

  const toggleLanguage = () => {
    i18n.changeLanguage(i18n.language === "en" ? "es" : "en");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 items-center justify-between px-4 md:px-8">
        <a href="#" className="font-bold text-primary text-lg">
          mp
        </a>

        <nav className="hidden md:flex items-center gap-6">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {t(item.key)}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          {/* Language toggle - stands out with primary color */}
          <Button
            onClick={toggleLanguage}
            variant="default"
            size="sm"
            className="gap-1.5 font-semibold"
          >
            <Globe className="size-4" />
            {i18n.language === "en" ? "ES" : "EN"}
          </Button>

          {/* Theme toggle */}
          <Button
            onClick={toggleTheme}
            variant="ghost"
            size="icon"
          >
            {theme === "light" ? (
              <Moon className="size-5" />
            ) : (
              <Sun className="size-5" />
            )}
            <span className="sr-only">Toggle theme</span>
          </Button>

          {/* Mobile menu */}
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger
              render={
                <Button variant="ghost" size="icon" className="md:hidden" />
              }
            >
              <Menu className="size-5" />
              <span className="sr-only">Open menu</span>
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              <div className="flex flex-col gap-4 mt-8">
                {navItems.map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className="text-lg text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {t(item.key)}
                  </a>
                ))}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
