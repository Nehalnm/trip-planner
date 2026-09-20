import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { getTripAnalytics } from "../api";

interface CategoryBreakdown {
  category: string;
  total: number;
}

interface PersonBreakdown {
  user_id: string;
  name: string;
  total_paid: number;
}

interface TripAnalytics {
  total_spent: number;
  by_category: CategoryBreakdown[];
  by_person: PersonBreakdown[];
}

function AnalyticsDashboard({ tripId }: { tripId: string }) {
  const [analytics, setAnalytics] = useState<TripAnalytics | null>(null);

  useEffect(() => {
    getTripAnalytics(tripId).then(setAnalytics);
  }, [tripId]);

  if (!analytics) return <p>Loading analytics...</p>;

  return (
    <div>
      <p><strong>Total Spent:</strong> ₹{analytics.total_spent.toFixed(2)}</p>

      <h4>By Category</h4>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={analytics.by_category}>
          <XAxis dataKey="category" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="total" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>

      <h4>By Person</h4>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={analytics.by_person}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="total_paid" fill="#82ca9d" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AnalyticsDashboard;