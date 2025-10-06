import Link from 'next/link';
import { cn } from '@/lib/utils';

interface NavItemProps {
  href: string;
  children: React.ReactNode;
  active?: boolean;
}

const NavItem = ({ href, children, active }: NavItemProps) => (
  <Link
    href={href}
    className={cn(
      'px-4 py-2 text-sm font-medium transition-colors hover:text-primary',
      active ? 'text-primary' : 'text-muted-foreground'
    )}
  >
    {children}
  </Link>
);

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold">NBA Fantasy Insights</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <NavItem href="/">Dashboard</NavItem>
            <NavItem href="/free-agents">Free Agents</NavItem>
            <NavItem href="/compare">Compare</NavItem>
            <NavItem href="/injuries">Injuries</NavItem>
          </nav>
        </div>
      </div>
    </header>
  );
}
