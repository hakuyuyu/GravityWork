import { useState, useRef, useEffect } from 'react';

// Define types based on backend ChatResponse
export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    intent?: 'triage' | 'action' | 'direct_answer';
    pending_action?: {
        action_id: string;
        action_type: string;
        description: string;
        parameters: any;
    };
    confidence?: float;
}

interface ChatResponse {
    response: string;
    intent: string;
    confidence: number;
    sources?: any[];
    requires_confirmation: boolean;
    pending_action?: any;
}

export function useChat() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'assistant',
            content: "Hello! I'm GravityWork. How can I help you orchestrate your project today?"
        }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const sendMessage = async (messageText: string) => {
        if (!messageText.trim()) return;

        // Add user message immediately
        const userMsg: ChatMessage = { role: 'user', content: messageText };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);
        setError(null);

        try {
            // POST to backend
            const response = await fetch('http://localhost:8000/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.statusText}`);
            }

            const data: ChatResponse = await response.json();

            // Add assistant response
            const assistantMsg: ChatMessage = {
                role: 'assistant',
                content: data.response,
                intent: data.intent as any,
                pending_action: data.pending_action,
                confidence: data.confidence
            };

            setMessages(prev => [...prev, assistantMsg]);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error connecting to the server." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleConfirmAction = async (actionId: string, approved: boolean) => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/chat/confirm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action_id: actionId, approved })
            });

            if (!response.ok) {
                throw new Error(`Confirmation failed: ${response.statusText}`);
            }

            const data = await response.json();

            // Add follow-up message from system
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: approved ? `✅ ${data.message}` : `❌ Action cancelled.`
            }]);

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Confirmation error');
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        input,
        setInput,
        sendMessage,
        isLoading,
        error,
        handleConfirmAction
    };
}
