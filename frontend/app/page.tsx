import { cn } from '../utils/cn';

export default function Home() {
    return (
        <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden">
            {/* LEFT SIDEBAR - Navigation & Projects (LeanWorks Style) */}
            <div className="w-64 border-r border-border bg-background/50 p-4 hidden md:flex flex-col">
                <div className="mb-6">
                    <h2 className="text-sm font-semibold text-muted-foreground mb-2">Projects</h2>
                    <div className="space-y-1">
                        <button className="w-full text-left px-3 py-2 rounded-md bg-accent text-accent-foreground text-sm font-medium">
                            Main Project
                        </button>
                        <button className="w-full text-left px-3 py-2 rounded-md hover:bg-muted text-muted-foreground text-sm transition-colors">
                            Mobile App Redesign
                        </button>
                    </div>
                </div>

                <div className="mt-auto">
                    <button className="w-full flex items-center px-3 py-2 rounded-md hover:bg-muted text-muted-foreground text-sm transition-colors">
                        <span>Settings</span>
                    </button>
                </div>
            </div>

            {/* CENTER - Chat Interface (LeanWorks Glow + Structure) */}
            <div className="flex-1 flex flex-col relative">
                {/* Glow Effect */}
                <div className="absolute inset-0 pointer-events-none ai-glow opacity-50" />

                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    <div className="max-w-3xl mx-auto space-y-6">
                        {/* Welcome Message */}
                        <div className="flex justify-start">
                            <div className="max-w-[80%] rounded-2xl rounded-tl-none bg-muted px-4 py-3 text-sm">
                                Hello! I'm GravityWork. How can I help you orchestrate your project today?
                            </div>
                        </div>

                        {/* User Message Example */}
                        <div className="flex justify-end">
                            <div className="max-w-[80%] rounded-2xl rounded-tr-none bg-primary text-primary-foreground px-4 py-3 text-sm">
                                What is the status of JIRA-100?
                            </div>
                        </div>
                    </div>
                </div>

                {/* Input Area */}
                <div className="p-4 border-t border-border bg-background/50 backdrop-blur">
                    <div className="max-w-3xl mx-auto relative">
                        <input
                            type="text"
                            placeholder="Ask about tickets, tasks, or sprints..."
                            className="w-full bg-background border border-input rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 shadow-sm"
                        />
                        <button className="absolute right-2 top-2 p-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M5 12h14M12 5l7 7-7 7" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            {/* RIGHT SIDEBAR - Quantitative Stats (ScaleAlpha Style) */}
            <div className="w-80 border-l border-border bg-background/50 p-4 hidden lg:flex flex-col overflow-y-auto">
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-4">Context</h3>

                {/* Sprint Velocity Card */}
                <div className="mb-4 rounded-lg border border-border bg-card p-3 shadow-sm">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-medium text-muted-foreground">Sprint Velocity</span>
                        <span className="text-xs font-bold text-green-500">▲ 12%</span>
                    </div>
                    <div className="text-2xl font-bold font-mono">42 SP</div>
                    <div className="h-1 w-full bg-muted mt-2 rounded-full overflow-hidden">
                        <div className="h-full bg-primary w-[70%]" />
                    </div>
                </div>

                {/* Ticket Stats Grid */}
                <div className="grid grid-cols-2 gap-2 mb-4">
                    <div className="rounded-lg border border-border bg-card p-3">
                        <div className="text-xs text-muted-foreground mb-1">Open</div>
                        <div className="text-xl font-bold">12</div>
                    </div>
                    <div className="rounded-lg border border-border bg-card p-3">
                        <div className="text-xs text-muted-foreground mb-1">Review</div>
                        <div className="text-xl font-bold text-yellow-500">5</div>
                    </div>
                </div>

                {/* Recent Activity */}
                <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-wider mb-2 mt-2">Activity</h3>
                <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex gap-2 text-xs">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0" />
                            <div>
                                <span className="font-semibold text-foreground">JIRA-10{i}</span>
                                <p className="text-muted-foreground">moved to In Progress</p>
                                <span className="text-[10px] text-muted-foreground opacity-70">2h ago</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
