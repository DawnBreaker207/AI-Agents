import {useTheme} from "next-themes";
import {Button} from "~/components/ui/button";
import {Moon, Sun} from "lucide-react";

export function ModeToggle() {
    const {theme, setTheme} = useTheme();

    return (
        <Button
            variant="ghost"
            size="icon"
            className="cursor-pointer"
            aria-label="Chuyển chế độ sáng/tối"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
            <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 motion-safe:transition-transform motion-safe:transition-opacity dark:-rotate-90 dark:scale-0"/>
            <Moon
                className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 motion-safe:transition-transform motion-safe:transition-opacity dark:rotate-0 dark:scale-100"/>
            <span className="sr-only">Toggle theme</span>
        </Button>
    )
}
