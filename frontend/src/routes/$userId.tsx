import { createFileRoute } from '@tanstack/react-router'
import { useState, useMemo, useTransition } from 'react'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "@/components/ui/combobox"
import {
  MagicWandIcon,
  QuotesIcon,
  SparkleIcon,
  ClockCounterClockwiseIcon,
  StarIcon,
  ChatCircleTextIcon,
  ArrowRightIcon
} from '@phosphor-icons/react'

import { recommendItems, simulateReview } from "@/lib/api"

// Local Data Imports
import personas from "../data/personas.json"
import history from "../data/history.json"
import metadata from "../data/movies_metadata.json"
import { toast } from 'sonner'

export const Route = createFileRoute('/$userId')({
  component: RouteComponent,
})

function RouteComponent() {
  const { userId } = Route.useParams()
  const [selectedMovie, setSelectedMovie] = useState<string | null>(null)

  // States for Task A (Simulation)
  const [isPending, startTransition] = useTransition()
  const [simulationResult, setSimulationResult] = useState<{ score: number, summary: string, text: string } | null>(null)

  // States for Task B (Recommendations)
  const [isRecPending, startRecTransition] = useTransition()
  const [recommendations, setRecommendations] = useState<{ reasoning: string, recommendations: any[] } | null>(null)

  const movieTitles = useMemo(() => Object.values(metadata), [])
  const persona = personas.find(p => p.userId === userId)
  const userHistory = history[userId as keyof typeof history] || []

  if (!persona) return <div className="p-8 text-center text-red-500">Persona Profile Not Found.</div>

  const handleSelect = (title: string) => {
    const entry = Object.entries(metadata).find(([_, v]) => v === title)
    if (entry) setSelectedMovie(entry[0])
  }

  // TASK A: Run Simulation
  const handleSimulate = () => {
    if (!selectedMovie) return
    startTransition(async () => {
      try {
        const data = await simulateReview({ userId, productId: selectedMovie })
        setSimulationResult(data)
      } catch (e) {
        console.error("Simulation failed", e)
        toast.error("Simulation Failed")
      }
    })
  }

  // TASK B: Run Recommendations
  const handleRecommend = () => {
    startRecTransition(async () => {
      try {
        const data = await recommendItems({ userId, conversationHistory: [] })
        setRecommendations(data)
      } catch (e) {
        console.error("Recommendation failed", e)
        toast.error("Recommendation Failed")

      }
    })
  }

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground p-6 md:p-12 gap-8 max-w-7xl mx-auto">

      {/* --- HEADER SECTION --- */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b pb-8 border-border/50">
        <div className="flex items-center gap-6">
          <div className="h-24 w-24 rounded-full border-4 border-primary/20 p-1">
            <img
              src={`https://api.dicebear.com/9.x/avataaars/svg?seed=${persona.profileName}`}
              alt="Avatar"
              className="rounded-full bg-muted"
            />
          </div>
          <div>
            <h1 className="text-4xl font-black tracking-tight uppercase italic">{persona.profileName}</h1>
            <div className="flex gap-2 mt-2">
              <Badge variant="default" className="font-bold italic">
                {persona.archetype}
              </Badge>
              <Badge variant="secondary">
                ID: {userId}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="bg-card border p-4 min-w-30">
            <p className="text-xs uppercase text-muted-foreground font-bold tracking-widest">Avg Rating</p>
            <p className="text-3xl font-black italic">{persona.stats.avgRating}</p>
          </div>
          <div className="bg-card border p-4 min-w-30">
            <p className="text-xs uppercase text-muted-foreground font-bold tracking-widest">Dataset Size</p>
            <p className="text-3xl font-black italic">{persona.stats.reviews} <span className="text-sm font-normal not-italic">Reviews</span></p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* --- LEFT COLUMN: HISTORY --- */}
        <aside className="lg:col-span-1 space-y-6">
          <div className="flex items-center gap-2 font-black uppercase text-sm tracking-tighter border-l-4 border-primary pl-3">
            <ClockCounterClockwiseIcon size={24} weight="bold" />
            <h2>Training History</h2>
          </div>
          <ScrollArea className="h-150 pr-4">
            <div className="space-y-4">
              {userHistory.map((item: any, i: number) => (
                <div key={i} className="p-5 bg-muted/30 border border-border/50 hover:border-primary/50 transition-colors group">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-black text-sm uppercase leading-tight group-hover:text-primary transition-colors">{item.title}</h3>
                    <div className="flex items-center text-yellow-500 font-bold text-sm bg-yellow-500/10 px-2 py-0.5">
                      <StarIcon weight="fill" className="mr-1" /> {item.score}
                    </div>
                  </div>
                  <p className="text-xs font-bold text-muted-foreground mb-2 underline decoration-primary/30 uppercase tracking-wide">
                    {item.summary}
                  </p>
                  <p className="text-xs leading-relaxed italic text-muted-foreground/80">
                    "{item.text}"
                  </p>
                </div>
              ))}
            </div>
          </ScrollArea>
        </aside>

        {/* --- RIGHT COLUMN: ACTIONS --- */}
        <main className="lg:col-span-2">
          <Tabs defaultValue="simulate" className="w-full">
            <TabsList className="grid w-full grid-cols-2 h-14 bg-muted p-1 border ">
              <TabsTrigger value="simulate" className="gap-2 font-bold uppercase  data-[state=active]:bg-background data-[state=active]:shadow-none">
                <MagicWandIcon size={20} /> Task A: Simulate
              </TabsTrigger>
              <TabsTrigger value="recommend" className="gap-2 font-bold uppercase  data-[state=active]:bg-background data-[state=active]:shadow-none">
                <SparkleIcon size={20} /> Task B: Recommend
              </TabsTrigger>
            </TabsList>

            {/* --- TASK A: SIMULATION TAB --- */}
            <TabsContent value="simulate" className="mt-8 space-y-8">
              <div className="bg-card border p-8 space-y-8 relative overflow-hidden">
                <div className="space-y-2 relative z-10">
                  <h3 className="text-2xl font-black uppercase italic tracking-tight">Synthetic Review Generation</h3>
                  <p className="text-sm text-muted-foreground">
                    Prompt the LLM to channel {persona.profileName.split(' ')[0]}'s cultural nuances for a new title.
                  </p>
                </div>

                <div className="flex flex-col gap-4 relative z-10">
                  <Combobox items={movieTitles} onValueChange={(value) => handleSelect(value as string)}>
                    <ComboboxInput
                      placeholder="Search the verified Amazon Archive..."
                      className="h-14 border-2 border-border focus:border-primary  bg-background text-lg font-medium"
                    />
                    <ComboboxContent>
                      <ComboboxEmpty>No match in archive.</ComboboxEmpty>
                      <ComboboxList>
                        {(item) => <ComboboxItem key={item} value={item}>{item}</ComboboxItem>}
                      </ComboboxList>
                    </ComboboxContent>
                  </Combobox>


                </div>

                <Button
                  className="w-full p-6 text-lg "
                  disabled={!selectedMovie || isPending}
                  onClick={handleSimulate}
                >
                  {isPending ? "Analysing Stylistic Nuance..." : "Initiate Simulation"}
                </Button>

                {/* Simulation Output Area */}
                <div className="min-h-60 bg-muted/20 border-2 border-dashed border-border/50 flex items-center justify-center p-8 transition-all">
                  {isPending ? (
                    <div className="text-center space-y-4">
                      <div className="flex justify-center gap-2">
                        {[1, 2, 3].map(i => <div key={i} className="w-3 h-3 bg-primary animate-bounce" style={{ animationDelay: `${i * 0.1}s` }} />)}
                      </div>
                      <p className="font-mono text-xs uppercase tracking-widest text-muted-foreground">Retrieving historical grounding...</p>
                    </div>
                  ) : simulationResult ? (
                    <div className="w-full space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                      <div className="flex justify-between items-center border-b border-primary/20 pb-4">
                        <Badge className=" px-4 py-1 text-lg font-black bg-primary">SCORE: {simulationResult.score} / 5</Badge>
                        <div className="text-[10px] font-mono text-muted-foreground uppercase">Output Verification: Llama-3.1-8B-Instant</div>
                      </div>
                      <div>
                        <h4 className="text-2xl font-black italic mb-3 leading-tight">"{simulationResult.summary}"</h4>
                        <p className="text-lg leading-relaxed text-foreground/90 font-medium font-serif">
                          {simulationResult.text}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center opacity-30 grayscale">
                      <QuotesIcon size={64} className="mx-auto mb-4" />
                      <p className="uppercase text-sm font-black tracking-widest">Awaiting Simulation Parameters</p>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>

            {/* --- TASK B: RECOMMENDATION TAB --- */}
            <TabsContent value="recommend" className="mt-8 space-y-8">
              <div className="bg-card border p-8 space-y-8">
                <div className="space-y-2">
                  <h3 className="text-2xl font-black uppercase italic tracking-tight">Reccomnded Movies</h3>
                  <p className="text-sm text-muted-foreground">
                    Semantic search engine cross-referencing Amazon history.
                  </p>
                </div>

                {!recommendations && !isRecPending && (
                  <div className="py-20 text-center border-2 border-dashed border-border/50">
                    <SparkleIcon size={48} className="mx-auto mb-4 text-primary opacity-50" />
                    <p className="mb-6 font-bold uppercase tracking-wide">Generate taste-aligned recommendations</p>
                    <Button onClick={handleRecommend} variant='link' className="text-base italic">Run TF-IDF Engine</Button>
                  </div>
                )}

                {isRecPending && (
                  <div className="py-20 text-center animate-pulse">
                    <p className="font-mono text-xs uppercase tracking-widest">Calculating Cosine Similarity...</p>
                  </div>
                )}

                {recommendations && (
                  <div className="space-y-8 animate-in fade-in duration-1000">
                    <div className="p-6 bg-primary/5 border-l-4 border-primary">
                      <h4 className="flex items-center gap-2 font-black uppercase text-sm mb-2">
                        <ChatCircleTextIcon weight="fill" /> Twin Reasoning:
                      </h4>
                      <p className="text-lg leading-relaxed italic opacity-90">
                        "{recommendations.reasoning}"
                      </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {recommendations.recommendations.map((rec: any, idx: number) => (
                        <div key={idx} className="p-4 border bg-muted/20 flex justify-between items-center group hover:bg-muted/40 transition-colors">
                          <div>
                            <span className="text-[10px] font-mono text-primary font-bold">RANK #{rec.rank}</span>
                            <h5 className="font-black uppercase text-md group-hover:translate-x-1 transition-transform">{rec.title}</h5>
                            <p className="text-[10px] text-muted-foreground uppercase tracking-widest">ASIN: {rec.productId}</p>
                          </div>
                          <ArrowRightIcon weight="bold" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  )
}
