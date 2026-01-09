'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Zap, Database, Bot } from 'lucide-react'

type IntentType = 'retrieval' | 'aggregation' | 'action' | 'clarification'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    intent?: IntentType
    sources?: string[]
    timestamp: string
}

const intentConfig: Record<IntentType, { icon: React.ReactNode; label: string; color: string }> = {
    retrieval: { icon: <Database className="w-3 h-3" />, label: 'Knowledge', color: 'text-blue-400' },
    aggregation: { icon: <Zap className="w-3 h-3" />, label: 'Aggregating', color: 'text-yellow-400' },
    action: { icon: <Bot className="w-3 h-3" />, label: 'Agent', color: 'text-green-400' },
    clarification: { icon: <Loader2 className="w-3 h-3" />, label: 'Clarifying', color: 'text-purple-400' },
}

export default function Home() {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "👋 Welcome to GravityWork! I can help you with:\n\n• **Search knowledge** - \"What's the status of PROJ-123?\"\n• **Aggregate insights** - \"Summarize the Slack discussion about the login bug\"\n• **Take actions** - \"Create a ticket for the API timeout issue\"\n\nHow can I help you today?",
            intent: 'retrieval',
            timestamp: new Date().toISOString(),
        }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!input.trim() || isLoading) return

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date().toISOString(),
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)

        try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input }),
            })

            if (response.ok) {
                const data = await response.json()
                const assistantMessage: Message = {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: data.message,
                    intent: data.intent,
                    sources: data.sources,
                    timestamp: data.timestamp,
                }
                setMessages(prev => [...prev, assistantMessage])
            } else {
                // Handle error
                setMessages(prev => [...prev, {
                    id: (Date.now() + 1).toString(),
                    role: 'assistant',
                    content: '⚠️ Sorry, I encountered an error. Please try again.',
                    timestamp: new Date().toISOString(),
                }])
            }
        } catch (error) {
            // Fallback for when backend is not running
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `🔧 **Backend not connected**\n\nTo get started, run:\n\`\`\`bash\ncd backend && pip install -r requirements.txt\npython main.py\n\`\`\`\n\nI received: "${input}"`,
                intent: 'clarification',
                timestamp: new Date().toISOString(),
            }])
        }

        setIsLoading(false)
    }

    return (
        <div className="max-w-4xl mx-auto px-4 py-8 h-[calc(100vh-140px)] flex flex-col">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">
                    AI-Native Project Intelligence
                </h1>
                <p className="text-gray-400">
                    Ask questions, get insights, and automate actions across Jira, Slack, and GitHub
                </p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} message-enter`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user'
                                    ? 'bg-gravity-600 text-white'
                                    : 'glass text-gray-100'
                                }`}
                        >
                            {/* Intent badge */}
                            {message.intent && message.role === 'assistant' && (
                                <div className={`flex items-center gap-1 text-xs mb-2 ${intentConfig[message.intent].color}`}>
                                    {intentConfig[message.intent].icon}
                                    <span>{intentConfig[message.intent].label}</span>
                                </div>
                            )}

                            {/* Message content */}
                            <div className="whitespace-pre-wrap text-sm leading-relaxed">
                                {message.content}
                            </div>

                            {/* Sources */}
                            {message.sources && message.sources.length > 0 && (
                                <div className="mt-2 pt-2 border-t border-white/10 text-xs text-gray-400">
                                    Sources: {message.sources.join(', ')}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {/* Loading indicator */}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="glass rounded-2xl px-4 py-3">
                            <div className="typing-indicator flex gap-1">
                                <span className="w-2 h-2 bg-gravity-500 rounded-full" />
                                <span className="w-2 h-2 bg-gravity-500 rounded-full" />
                                <span className="w-2 h-2 bg-gravity-500 rounded-full" />
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="relative">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about your projects, or tell me to take an action..."
                    className="w-full px-4 py-4 pr-12 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gravity-500 focus:border-transparent transition-all"
                    disabled={isLoading}
                />
                <button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-gravity-600 hover:bg-gravity-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    {isLoading ? (
                        <Loader2 className="w-5 h-5 text-white animate-spin" />
                    ) : (
                        <Send className="w-5 h-5 text-white" />
                    )}
                </button>
            </form>
        </div>
    )
}
