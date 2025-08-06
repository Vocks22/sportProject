import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Mardi 6 Août 2025</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Test Card</CardTitle>
        </CardHeader>
        <CardContent>
          <p>L'application fonctionne !</p>
        </CardContent>
      </Card>
    </div>
  )
}

