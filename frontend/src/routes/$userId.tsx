import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from "@/components/ui/tabs" // Assuming your shadcn path
import { Button } from "@/components/ui/button"
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group"
import { ScrollArea } from "@/components/ui/scroll-area"
// import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import {
  MagicWandIcon,
  QuotesIcon,
  SparkleIcon,
  ClockCounterClockwiseIcon,
  MagnifyingGlassIcon,
} from '@phosphor-icons/react'

// Local Data Imports
import personas from "../data/personas.json"
import history from "../data/history.json"
import metadata from "../data/movies_metadata.json"

export const Route = createFileRoute('/$userId')({
  component: RouteComponent,
})

function RouteComponent() {
  const { userId } = Route.useParams()
  const [selectedMovie, setSelectedMovie] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  // Find the persona details from our JSON
  const persona = personas.find(p => p.userId === userId)
  const userHistory = history[userId as keyof typeof history] || []

  if (!persona) return <div className="p-8 text-center">Persona not found.</div>

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground p-6 md:p-12 gap-8 max-w-7xl mx-auto">

      {/* --- HEADER SECTION --- */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="flex items-center gap-4">
          <div className="h-20 w-20 rounded-full border-2 border-border overflow-hidden bg-muted">
            <img src={`https://api.dicebear.com/9.x/avataaars/svg?seed=${persona.profileName}`} alt="Avatar" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{persona.profileName}</h1>
            <div className="flex gap-2 mt-1">
              <Badge variant="outline" className="capitalize">{persona.archetype}</Badge>
              <Badge variant="secondary">ID: {userId}</Badge>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm bg-card p-4 border">
          <div className="text-muted-foreground text-center px-2">
            <p className="font-bold text-foreground">{persona.stats.avgRating}</p>
            <p>Avg Score</p>
          </div>
          <div className="text-muted-foreground text-center px-2">
            <p className="font-bold text-foreground">{persona.stats.reviews}</p>
            <p>Reviews</p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

        {/* --- LEFT COLUMN: HISTORY --- */}
        <aside className="lg:col-span-1 space-y-4">
          <div className="flex items-center gap-2 font-semibold mb-2 text-muted-foreground">
            <ClockCounterClockwiseIcon size={20} />
            <h2>Historical Grounding</h2>
          </div>
          <ScrollArea className="h-150 pr-4 ">
            <div className="space-y-4">
              {userHistory.map((item: any, i: number) => (
                <div key={i} className="p-4 bg-muted/40 border space-y-2">
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-sm leading-tight">{item.title}</h3>
                    <Badge className="bg-yellow-500/10 text-yellow-500 border-none shrink-0">★ {item.score}</Badge>
                  </div>
                  <p className="text-xs font-semibold uppercase text-muted-foreground">"{item.summary}"</p>
                  <p className="text-xs text-muted-foreground line-clamp-3">"{item.text}"</p>
                </div>
              ))}
            </div>
          </ScrollArea>
        </aside>

        {/* --- RIGHT COLUMN: ACTIONS --- */}
        <main className="lg:col-span-2">
          <Tabs defaultValue="simulate" className="w-full">
            <TabsList className="grid w-full grid-cols-2 h-12">
              <TabsTrigger value="simulate" className="gap-2">
                <MagicWandIcon size={18} /> Simulate
              </TabsTrigger>
              <TabsTrigger value="recommend" className="gap-2">
                <SparkleIcon size={18} /> Recommendations
              </TabsTrigger>
            </TabsList>

            {/* TASK A: SIMULATE */}
            <TabsContent value="simulate" className="mt-6 space-y-6">
              <div className="bg-card border p-6 space-y-6">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">Draft a Synthetic Review</h3>
                  <p className="text-sm text-muted-foreground">
                    Select a movie from the archive to see how {persona.profileName.split(' ')[0]} would react.
                  </p>
                </div>

                <InputGroup className="">
                  <InputGroupAddon>
                    <MagnifyingGlassIcon />
                  </InputGroupAddon>
                  <InputGroupInput placeholder="Search..." />
                  {/* <InputGroupAddon align="inline-end">12 results</InputGroupAddon> */}
                </InputGroup>

                <div className="flex flex-wrap gap-2">
                  {Object.entries(metadata).slice(0, 8).map(([id, title]) => (
                    <Button
                      key={id}
                      variant={selectedMovie === id ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedMovie(id)}
                    >
                      {title as string}
                    </Button>
                  ))}
                </div>

                <Button className="w-full h-12 text-lg gap-2" disabled={!selectedMovie}>
                  Generate Twin Review
                </Button>

                {/* Response Placeholder */}
                <div className="min-h-50 border-2 border-dashed  flex items-center justify-center p-8 text-center">
                  <div className="space-y-2">
                    <QuotesIcon size={32} className="mx-auto text-muted-foreground/20" />
                    <p className="text-muted-foreground italic text-sm">Synthetic output will appear here...</p>
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* TASK B: RECOMMEND */}
            <TabsContent value="recommend" className="mt-6">
              <div className="bg-card border p-6 text-center py-20">
                <p className="text-muted-foreground">Ready to bridge {persona.profileName.split(' ')[0]}'s taste with Nollywood?</p>
                <Button variant="link">Run Task B Engine</Button>
              </div>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
}