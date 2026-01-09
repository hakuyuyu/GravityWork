import { useState, useEffect } from 'react';

export interface DashboardStats {
    velocity: {
        value: string;
        trend: string;
        trend_direction: 'up' | 'down';
    };
    active_tickets: {
        value: number;
        label: string;
    };
    attention_needed: {
        value: number;
        label: string;
        status: 'success' | 'warning' | 'danger';
    };
    completion_rate: number;
}

export interface ActivityItem {
    id: number;
    project: string;
    action: string;
    time: string;
    type: 'jira' | 'github' | 'slack';
}

export function useDashboard() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [activity, setActivity] = useState<ActivityItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchDashboardData = async () => {
        try {
            setIsLoading(true);
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

            // Parallel fetch
            const [statsRes, activityRes] = await Promise.all([
                fetch(`${baseUrl}/api/dashboard/stats`),
                fetch(`${baseUrl}/api/dashboard/activity`)
            ]);

            if (!statsRes.ok || !activityRes.ok) {
                throw new Error('Failed to fetch dashboard data');
            }

            const statsData = await statsRes.json();
            const activityData = await activityRes.json();

            setStats(statsData);
            setActivity(activityData.activities);
            setError(null);
        } catch (err) {
            console.error(err);
            setError('Failed to load dashboard');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();

        // Poll every 30 seconds
        const interval = setInterval(fetchDashboardData, 30000);
        return () => clearInterval(interval);
    }, []);

    return { stats, activity, isLoading, error, refresh: fetchDashboardData };
}
