import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { cn } from '../utils/cn';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
    title: 'GravityWork | AI Project Orchestration',
    description: 'Federated Context AI Agent for Project Management',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={cn(inter.className, "min-h-screen bg-background antialiased")}>
                <nav className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
                    <div className="flex h-14 items-center px-4">
                        <div className="mr-4 hidden md:flex">
                            <span className="text-lg font-bold text-primary">GravityWork</span>
                        </div>
                        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                            <div className="w-full flex-1 md:w-auto md:flex-none">
                                {/* Search placeholder */}
                            </div>
                            <nav className="flex items-center space-x-2">
                                <span className="text-sm font-medium text-muted-foreground mr-2">Workspace: Main</span>
                                <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary text-xs font-bold">
                                    JS
                                </div>
                            </nav>
                        </div>
                    </div>
                </nav>
                <main className="flex-1">
                    {children}
                </main>
            </body>
        </html>
    );
}
