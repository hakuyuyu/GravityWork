import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'GravityWork - AI-Native Project Orchestration',
    description: 'Aggregate Jira, Slack, and GitHub into a single intelligence layer',
    keywords: ['AI', 'Project Management', 'Automation', 'Jira', 'Slack', 'GitHub'],
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.className} min-h-screen bg-gradient-to-br from-gravity-950 via-gray-900 to-gravity-900`}>
                <div className="flex flex-col min-h-screen">
                    {/* Navigation */}
                    <nav className="border-b border-white/10 backdrop-blur-md bg-black/20">
                        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                            <div className="flex items-center justify-between h-16">
                                <div className="flex items-center gap-2">
                                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gravity-500 to-gravity-700 flex items-center justify-center">
                                        <span className="text-white font-bold text-sm">G</span>
                                    </div>
                                    <span className="text-white font-semibold text-lg">GravityWork</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <button className="text-gray-400 hover:text-white transition-colors">
                                        Dashboard
                                    </button>
                                    <button className="text-gray-400 hover:text-white transition-colors">
                                        Integrations
                                    </button>
                                    <button className="px-4 py-2 rounded-lg bg-gravity-600 hover:bg-gravity-500 text-white text-sm font-medium transition-colors">
                                        Settings
                                    </button>
                                </div>
                            </div>
                        </div>
                    </nav>

                    {/* Main Content */}
                    <main className="flex-1">
                        {children}
                    </main>

                    {/* Footer */}
                    <footer className="border-t border-white/10 py-4">
                        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
                            GravityWork © 2025 - AI-Native Project Orchestration
                        </div>
                    </footer>
                </div>
            </body>
        </html>
    )
}
