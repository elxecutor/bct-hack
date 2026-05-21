import { createFileRoute, Link } from "@tanstack/react-router"
import { Badge } from "@/components/ui/badge"
import { ChatCenteredTextIcon, StarIcon, CalendarIcon } from '@phosphor-icons/react'
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import personas from "../data/personas.json"
import { Card, CardContent, CardHeader } from "@/components/ui/card"

export const Route = createFileRoute("/")({ component: App })

function App() {
  return (
    <div className="flex min-h-svh p-8 md:px-16 text-base">
      <div className="flex flex-col gap-4 w-full">
        <h1 className="text-3xl">CineTwin</h1>
        <p className="text-lg text-muted-foreground">
          Personae Dashboard
        </p>
        <div className="grid grid-cols-3 w-full gap-4 mt-8">
          {personas.map((persona) => (
            <Link to={`/$userId`} key={persona.userId} params={
              { userId: persona.userId }
            }>
              <Card className="border border-border hover:border-primary/50">
                <CardHeader className="flex items-center gap-2">
                  <Avatar size="lg">
                    <AvatarImage src={`https://api.dicebear.com/9.x/avataaars/svg?seed=${persona.profileName}`} />
                    <AvatarFallback>{persona.profileName.charAt(0)}</AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <h2 className="text-xl">{persona.profileName}</h2>
                    <p className="text-base text-muted-foreground">{persona.archetype}</p>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  <div className="flex gap-2 items-center">
                    <Badge variant="default" className="text-sm">
                      <ChatCenteredTextIcon size={56} />
                      {persona.stats.reviews}</Badge>
                    <Badge variant="default" className="text-sm">
                      <StarIcon size={56} />
                      {persona.stats.avgRating}</Badge>
                    <Badge variant="default" className="text-sm">
                      <CalendarIcon size={56} />
                      {persona.stats.since}</Badge>
                  </div>
                  <p className="text-base italic text-muted-foreground">"{persona.voiceSnippet}"</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div >
  )
}
