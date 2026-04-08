import { useState } from 'react'
import { toast } from 'sonner'
import { PageHeader } from '@/shared/components/PageHeader'
import { Button } from '@/shared/components/ui/button'
import { ButtonGroup } from '@/shared/components/ui/button-group'
import { Input } from '@/shared/components/ui/input'
import { Textarea } from '@/shared/components/ui/textarea'
import { Label } from '@/shared/components/ui/label'
import { Badge } from '@/shared/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/shared/components/ui/alert'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/shared/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/components/ui/tabs'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/shared/components/ui/accordion'
import { Avatar, AvatarFallback } from '@/shared/components/ui/avatar'
import { Checkbox } from '@/shared/components/ui/checkbox'
import { Switch } from '@/shared/components/ui/switch'
import { Slider } from '@/shared/components/ui/slider'
import { Progress } from '@/shared/components/ui/progress'
import { Separator } from '@/shared/components/ui/separator'
import { Spinner } from '@/shared/components/ui/spinner'
import { Skeleton } from '@/shared/components/ui/skeleton'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/shared/components/ui/tooltip'
import { Popover, PopoverContent, PopoverTrigger } from '@/shared/components/ui/popover'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/components/ui/dialog'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/shared/components/ui/sheet'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/components/ui/table'
import { Calendar } from '@/shared/components/ui/calendar'
import {
  Combobox,
  ComboboxInput,
  ComboboxContent,
  ComboboxList,
  ComboboxItem,
  ComboboxEmpty,
} from '@/shared/components/ui/combobox'
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from '@/shared/components/ui/command'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/shared/components/ui/carousel'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/shared/components/ui/breadcrumb'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/shared/components/ui/pagination'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/shared/components/ui/resizable'
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from '@/shared/components/ui/drawer'
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSeparator,
  InputOTPSlot,
} from '@/shared/components/ui/input-otp'
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarShortcut,
  MenubarTrigger,
} from '@/shared/components/ui/menubar'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from '@/shared/components/ui/context-menu'
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@/shared/components/ui/hover-card'
import { Kbd, KbdGroup } from '@/shared/components/ui/kbd'
import { ScrollArea } from '@/shared/components/ui/scroll-area'

// ─── Section wrapper ──────────────────────────────────────────────────────────
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <h2 className="text-lg font-semibold border-b pb-2">{title}</h2>
      {children}
    </section>
  )
}

// ─── Static data ─────────────────────────────────────────────────────────────
const TABLE_DATA = [
  { id: 1, name: 'Alpha Item', status: 'Active', created: '2024-01-15' },
  { id: 2, name: 'Beta Item', status: 'Pending', created: '2024-02-08' },
  { id: 3, name: 'Gamma Item', status: 'Inactive', created: '2024-03-22' },
]

const SCROLL_ITEMS = Array.from({ length: 20 }, (_, i) => `Item ${i + 1}`)

const FRAMEWORKS = [
  { value: 'react', label: 'React' },
  { value: 'vue', label: 'Vue' },
  { value: 'svelte', label: 'Svelte' },
  { value: 'angular', label: 'Angular' },
  { value: 'solid', label: 'SolidJS' },
]

// ─── Main component ───────────────────────────────────────────────────────────
export default function ShowcasePage() {
  const [progress, setProgress] = useState(60)
  const [sliderValue, setSliderValue] = useState([40])
  const [switchOn, setSwitchOn] = useState(false)
  const [checked, setChecked] = useState(false)
  const [calendarDate, setCalendarDate] = useState<Date | undefined>(new Date())
  const [commandOpen, setCommandOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(3)

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background">
        <div className="container mx-auto max-w-4xl py-8 px-4 space-y-12">
          <PageHeader
            title="Component Showcase"
            description="A living reference for every shadcn/ui component in this project."
            actions={
              <Button variant="outline" size="sm" onClick={() => window.history.back()}>
                ← Back
              </Button>
            }
          />

          {/* ── COLORS ──────────────────────────────────────────────────────── */}
          <Section title="Color Tokens">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {[
                { name: 'background', bg: 'bg-background', fg: 'text-foreground', label: 'Background' },
                { name: 'foreground', bg: 'bg-foreground', fg: 'text-background', label: 'Foreground' },
                { name: 'primary', bg: 'bg-primary', fg: 'text-primary-foreground', label: 'Primary' },
                { name: 'primary-foreground', bg: 'bg-primary-foreground', fg: 'text-primary', label: 'Primary FG' },
                { name: 'secondary', bg: 'bg-secondary', fg: 'text-secondary-foreground', label: 'Secondary' },
                { name: 'muted', bg: 'bg-muted', fg: 'text-muted-foreground', label: 'Muted' },
                { name: 'accent', bg: 'bg-accent', fg: 'text-accent-foreground', label: 'Accent' },
                { name: 'destructive', bg: 'bg-destructive', fg: 'text-white', label: 'Destructive' },
                { name: 'card', bg: 'bg-card', fg: 'text-card-foreground', label: 'Card' },
                { name: 'popover', bg: 'bg-popover', fg: 'text-popover-foreground', label: 'Popover' },
                { name: 'border', bg: 'bg-border', fg: 'text-foreground', label: 'Border' },
                { name: 'input', bg: 'bg-input', fg: 'text-foreground', label: 'Input' },
                { name: 'ring', bg: 'bg-ring', fg: 'text-background', label: 'Ring' },
              ].map(({ bg, fg, label, name }) => (
                <div key={name} className="flex flex-col overflow-hidden rounded-md border">
                  <div className={`h-12 ${bg}`} />
                  <div className="px-2 py-1.5 text-xs">
                    <div className="font-medium">{label}</div>
                    <div className="text-muted-foreground font-mono">--{name}</div>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          {/* ── BREADCRUMB ──────────────────────────────────────────────────── */}
          <Section title="Breadcrumb">
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="#">Home</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbLink href="#">Components</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator />
                <BreadcrumbItem>
                  <BreadcrumbPage>Showcase</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </Section>

          {/* ── BUTTONS ─────────────────────────────────────────────────────── */}
          <Section title="Buttons">
            <div className="flex flex-wrap gap-2 items-center">
              <Button>Default</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="link">Link</Button>
            </div>
            <div className="flex flex-wrap gap-2 items-center">
              <Button size="sm">Small</Button>
              <Button size="default">Default</Button>
              <Button size="lg">Large</Button>
              <Button size="icon">+</Button>
              <Button disabled>Disabled</Button>
              <Button disabled>
                <Spinner className="mr-2 h-4 w-4" />
                Loading
              </Button>
            </div>
            <div>
              <ButtonGroup>
                <Button variant="outline">Left</Button>
                <Button variant="outline">Center</Button>
                <Button variant="outline">Right</Button>
              </ButtonGroup>
            </div>
          </Section>

          {/* ── BADGES ──────────────────────────────────────────────────────── */}
          <Section title="Badges">
            <div className="flex flex-wrap gap-2">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
            </div>
          </Section>

          {/* ── AVATARS ─────────────────────────────────────────────────────── */}
          <Section title="Avatars">
            <div className="flex gap-3 items-center">
              <Avatar className="h-8 w-8">
                <AvatarFallback>JD</AvatarFallback>
              </Avatar>
              <Avatar className="h-10 w-10">
                <AvatarFallback>AB</AvatarFallback>
              </Avatar>
              <Avatar className="h-12 w-12">
                <AvatarFallback className="bg-primary text-primary-foreground">XY</AvatarFallback>
              </Avatar>
            </div>
          </Section>

          {/* ── KBD ─────────────────────────────────────────────────────────── */}
          <Section title="Keyboard (Kbd)">
            <div className="flex flex-wrap gap-3 items-center">
              <Kbd>⌘</Kbd>
              <Kbd>Enter</Kbd>
              <Kbd>Esc</Kbd>
              <KbdGroup>
                <Kbd>⌘</Kbd>
                <Kbd>K</Kbd>
              </KbdGroup>
              <KbdGroup>
                <Kbd>Ctrl</Kbd>
                <Kbd>Shift</Kbd>
                <Kbd>P</Kbd>
              </KbdGroup>
              <span className="text-sm text-muted-foreground">
                Open command palette with <Kbd>⌘</Kbd><Kbd>K</Kbd>
              </span>
            </div>
          </Section>

          {/* ── MENUBAR ─────────────────────────────────────────────────────── */}
          <Section title="Menubar">
            <Menubar>
              <MenubarMenu>
                <MenubarTrigger>File</MenubarTrigger>
                <MenubarContent>
                  <MenubarItem>New <MenubarShortcut>⌘N</MenubarShortcut></MenubarItem>
                  <MenubarItem>Open <MenubarShortcut>⌘O</MenubarShortcut></MenubarItem>
                  <MenubarSeparator />
                  <MenubarItem>Save <MenubarShortcut>⌘S</MenubarShortcut></MenubarItem>
                </MenubarContent>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger>Edit</MenubarTrigger>
                <MenubarContent>
                  <MenubarItem>Undo <MenubarShortcut>⌘Z</MenubarShortcut></MenubarItem>
                  <MenubarItem>Redo <MenubarShortcut>⌘Y</MenubarShortcut></MenubarItem>
                  <MenubarSeparator />
                  <MenubarItem>Cut</MenubarItem>
                  <MenubarItem>Copy</MenubarItem>
                  <MenubarItem>Paste</MenubarItem>
                </MenubarContent>
              </MenubarMenu>
              <MenubarMenu>
                <MenubarTrigger>View</MenubarTrigger>
                <MenubarContent>
                  <MenubarItem>Zoom In</MenubarItem>
                  <MenubarItem>Zoom Out</MenubarItem>
                  <MenubarSeparator />
                  <MenubarItem>Full Screen</MenubarItem>
                </MenubarContent>
              </MenubarMenu>
            </Menubar>
          </Section>

          {/* ── FORM CONTROLS ───────────────────────────────────────────────── */}
          <Section title="Form Controls">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg">
              <div className="space-y-1">
                <Label htmlFor="demo-input">Input</Label>
                <Input id="demo-input" placeholder="Type something..." />
              </div>
              <div className="space-y-1">
                <Label htmlFor="demo-select">Select</Label>
                <Select>
                  <SelectTrigger id="demo-select">
                    <SelectValue placeholder="Pick one…" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="a">Option A</SelectItem>
                    <SelectItem value="b">Option B</SelectItem>
                    <SelectItem value="c">Option C</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="demo-textarea">Textarea</Label>
                <Textarea id="demo-textarea" placeholder="Longer text…" rows={3} />
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="demo-checkbox"
                  checked={checked}
                  onCheckedChange={(v) => setChecked(Boolean(v))}
                />
                <Label htmlFor="demo-checkbox">Checkbox ({checked ? 'on' : 'off'})</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch id="demo-switch" checked={switchOn} onCheckedChange={setSwitchOn} />
                <Label htmlFor="demo-switch">Switch ({switchOn ? 'on' : 'off'})</Label>
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Slider — {sliderValue[0]}</Label>
                <Slider value={sliderValue} onValueChange={setSliderValue} min={0} max={100} step={1} />
              </div>
            </div>
          </Section>

          {/* ── INPUT OTP ───────────────────────────────────────────────────── */}
          <Section title="Input OTP">
            <div className="space-y-4">
              <div className="space-y-1">
                <Label>6-digit code</Label>
                <InputOTP maxLength={6}>
                  <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                  </InputOTPGroup>
                  <InputOTPSeparator />
                  <InputOTPGroup>
                    <InputOTPSlot index={3} />
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                  </InputOTPGroup>
                </InputOTP>
              </div>
            </div>
          </Section>

          {/* ── COMBOBOX ────────────────────────────────────────────────────── */}
          <Section title="Combobox">
            <div className="space-y-1 max-w-xs">
              <Label>Framework</Label>
              <Combobox>
                <ComboboxInput placeholder="Search framework…" />
                <ComboboxContent>
                  <ComboboxList>
                    <ComboboxEmpty>No results found.</ComboboxEmpty>
                    {FRAMEWORKS.map((f) => (
                      <ComboboxItem key={f.value} value={f.value}>
                        {f.label}
                      </ComboboxItem>
                    ))}
                  </ComboboxList>
                </ComboboxContent>
              </Combobox>
            </div>
          </Section>

          {/* ── COMMAND ─────────────────────────────────────────────────────── */}
          <Section title="Command Palette">
            <div className="space-y-3">
              <Button variant="outline" onClick={() => setCommandOpen(true)}>
                Open Command Palette <Kbd className="ml-2">⌘K</Kbd>
              </Button>
              <Card className="max-w-md">
                <CardContent className="p-0">
                  <Command>
                    <CommandInput placeholder="Type a command or search…" />
                    <CommandList>
                      <CommandEmpty>No results found.</CommandEmpty>
                      <CommandGroup heading="Suggestions">
                        <CommandItem>Dashboard <CommandShortcut>⌘D</CommandShortcut></CommandItem>
                        <CommandItem>Profile <CommandShortcut>⌘P</CommandShortcut></CommandItem>
                        <CommandItem>Settings <CommandShortcut>⌘S</CommandShortcut></CommandItem>
                      </CommandGroup>
                      <CommandSeparator />
                      <CommandGroup heading="Actions">
                        <CommandItem>Create Item</CommandItem>
                        <CommandItem>Export Data</CommandItem>
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </CardContent>
              </Card>
            </div>
            <CommandDialog open={commandOpen} onOpenChange={setCommandOpen}>
              <CommandInput placeholder="Type a command or search…" />
              <CommandList>
                <CommandEmpty>No results found.</CommandEmpty>
                <CommandGroup heading="Pages">
                  <CommandItem onSelect={() => setCommandOpen(false)}>Dashboard</CommandItem>
                  <CommandItem onSelect={() => setCommandOpen(false)}>Profile</CommandItem>
                  <CommandItem onSelect={() => setCommandOpen(false)}>Admin Users</CommandItem>
                </CommandGroup>
                <CommandSeparator />
                <CommandGroup heading="Actions">
                  <CommandItem onSelect={() => setCommandOpen(false)}>Create Item</CommandItem>
                  <CommandItem onSelect={() => setCommandOpen(false)}>Log out</CommandItem>
                </CommandGroup>
              </CommandList>
            </CommandDialog>
          </Section>

          {/* ── CALENDAR ────────────────────────────────────────────────────── */}
          <Section title="Calendar">
            <Card className="w-fit">
              <CardContent className="p-3">
                <Calendar mode="single" selected={calendarDate} onSelect={setCalendarDate} />
              </CardContent>
            </Card>
            {calendarDate && (
              <p className="text-sm text-muted-foreground">
                Selected: {calendarDate.toLocaleDateString()}
              </p>
            )}
          </Section>

          {/* ── CAROUSEL ────────────────────────────────────────────────────── */}
          <Section title="Carousel">
            <div className="px-12">
              <Carousel opts={{ align: 'start', loop: true }}>
                <CarouselContent>
                  {Array.from({ length: 5 }, (_, i) => (
                    <CarouselItem key={i} className="basis-1/3">
                      <Card>
                        <CardContent className="flex aspect-square items-center justify-center p-6">
                          <span className="text-3xl font-bold">{i + 1}</span>
                        </CardContent>
                      </Card>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                <CarouselPrevious />
                <CarouselNext />
              </Carousel>
            </div>
          </Section>

          {/* ── PROGRESS / SPINNER / SKELETON ───────────────────────────────── */}
          <Section title="Progress, Spinner & Skeleton">
            <div className="space-y-4 max-w-sm">
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{progress}%</span>
                </div>
                <Progress value={progress} />
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => setProgress((p) => Math.max(0, p - 10))}>
                    -10
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => setProgress((p) => Math.min(100, p + 10))}>
                    +10
                  </Button>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Spinner className="h-4 w-4" />
                <Spinner className="h-6 w-6" />
                <Spinner className="h-8 w-8" />
                <span className="text-sm text-muted-foreground">Spinners</span>
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            </div>
          </Section>

          {/* ── ALERTS ──────────────────────────────────────────────────────── */}
          <Section title="Alerts">
            <div className="space-y-3">
              <Alert>
                <AlertTitle>Default</AlertTitle>
                <AlertDescription>This is a default informational alert message.</AlertDescription>
              </Alert>
              <Alert variant="destructive">
                <AlertTitle>Destructive</AlertTitle>
                <AlertDescription>Something went wrong. Please try again.</AlertDescription>
              </Alert>
            </div>
          </Section>

          {/* ── CARDS ───────────────────────────────────────────────────────── */}
          <Section title="Cards">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Card Title</CardTitle>
                  <CardDescription>Supporting description text goes here.</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Card body content. You can put anything here — tables, charts, forms, etc.
                  </p>
                </CardContent>
                <CardFooter className="gap-2">
                  <Button size="sm">Action</Button>
                  <Button size="sm" variant="outline">Cancel</Button>
                </CardFooter>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Stats Card</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">1,248</div>
                  <p className="text-xs text-muted-foreground mt-1">+12% from last month</p>
                </CardContent>
              </Card>
            </div>
          </Section>

          {/* ── TABS ────────────────────────────────────────────────────────── */}
          <Section title="Tabs">
            <Tabs defaultValue="overview">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="settings">Settings</TabsTrigger>
                <TabsTrigger value="activity">Activity</TabsTrigger>
              </TabsList>
              <TabsContent value="overview" className="mt-4">
                <Card><CardContent className="pt-4 text-sm">Overview tab content.</CardContent></Card>
              </TabsContent>
              <TabsContent value="settings" className="mt-4">
                <Card><CardContent className="pt-4 text-sm">Settings tab content.</CardContent></Card>
              </TabsContent>
              <TabsContent value="activity" className="mt-4">
                <Card><CardContent className="pt-4 text-sm">Activity tab content.</CardContent></Card>
              </TabsContent>
            </Tabs>
          </Section>

          {/* ── ACCORDION ───────────────────────────────────────────────────── */}
          <Section title="Accordion">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>What is this project?</AccordionTrigger>
                <AccordionContent>
                  A full-stack architecture sample app with a React frontend and FastAPI backend.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Which UI library is used?</AccordionTrigger>
                <AccordionContent>
                  shadcn/ui — beautifully-designed components built on Radix UI and Tailwind CSS.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Can I customise these components?</AccordionTrigger>
                <AccordionContent>
                  Yes — every file lives in your repo under src/shared/components/ui/. Edit them to build your own design system.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </Section>

          {/* ── TABLE ───────────────────────────────────────────────────────── */}
          <Section title="Table">
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">#</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {TABLE_DATA.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell className="font-mono text-xs">{row.id}</TableCell>
                      <TableCell className="font-medium">{row.name}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            row.status === 'Active' ? 'default' :
                            row.status === 'Pending' ? 'secondary' : 'outline'
                          }
                        >
                          {row.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">{row.created}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          </Section>

          {/* ── SCROLL AREA ─────────────────────────────────────────────────── */}
          <Section title="Scroll Area">
            <Card className="max-w-xs">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Scrollable List</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ScrollArea className="h-48 px-4">
                  <div className="py-2 space-y-1">
                    {SCROLL_ITEMS.map((item) => (
                      <div key={item} className="text-sm py-1 border-b last:border-0">
                        {item}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </Section>

          {/* ── RESIZABLE ───────────────────────────────────────────────────── */}
          <Section title="Resizable Panels">
            <div className="h-32 rounded-md border overflow-hidden">
              <ResizablePanelGroup direction="horizontal">
                <ResizablePanel defaultSize={50}>
                  <div className="flex h-full items-center justify-center p-4 text-sm text-muted-foreground">
                    Left panel
                  </div>
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={50}>
                  <div className="flex h-full items-center justify-center p-4 text-sm text-muted-foreground">
                    Right panel
                  </div>
                </ResizablePanel>
              </ResizablePanelGroup>
            </div>
          </Section>

          {/* ── PAGINATION ──────────────────────────────────────────────────── */}
          <Section title="Pagination">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    href="#"
                    onClick={(e) => { e.preventDefault(); setCurrentPage((p) => Math.max(1, p - 1)) }}
                  />
                </PaginationItem>
                {[1, 2, 3, 4, 5].map((page) => (
                  <PaginationItem key={page}>
                    <PaginationLink
                      href="#"
                      isActive={page === currentPage}
                      onClick={(e) => { e.preventDefault(); setCurrentPage(page) }}
                    >
                      {page}
                    </PaginationLink>
                  </PaginationItem>
                ))}
                <PaginationItem>
                  <PaginationEllipsis />
                </PaginationItem>
                <PaginationItem>
                  <PaginationNext
                    href="#"
                    onClick={(e) => { e.preventDefault(); setCurrentPage((p) => Math.min(10, p + 1)) }}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </Section>

          {/* ── OVERLAYS ────────────────────────────────────────────────────── */}
          <Section title="Overlays — Dialog, Sheet, Drawer & Dropdown">
            <div className="flex flex-wrap gap-2">
              {/* Dialog */}
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline">Dialog</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Confirm action</DialogTitle>
                    <DialogDescription>This is a modal dialog. Confirm or cancel below.</DialogDescription>
                  </DialogHeader>
                  <p className="text-sm text-muted-foreground">Dialog body content.</p>
                  <DialogFooter>
                    <Button variant="outline">Cancel</Button>
                    <Button>Confirm</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>

              {/* Sheet */}
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline">Sheet</Button>
                </SheetTrigger>
                <SheetContent>
                  <SheetHeader>
                    <SheetTitle>Side Sheet</SheetTitle>
                    <SheetDescription>Slides in from the right.</SheetDescription>
                  </SheetHeader>
                  <div className="mt-4 text-sm text-muted-foreground">Sheet body content.</div>
                </SheetContent>
              </Sheet>

              {/* Drawer */}
              <Drawer>
                <DrawerTrigger asChild>
                  <Button variant="outline">Drawer</Button>
                </DrawerTrigger>
                <DrawerContent>
                  <DrawerHeader>
                    <DrawerTitle>Bottom Drawer</DrawerTitle>
                    <DrawerDescription>Slides up from the bottom. Great for mobile.</DrawerDescription>
                  </DrawerHeader>
                  <div className="px-4 text-sm text-muted-foreground">Drawer body content.</div>
                  <DrawerFooter>
                    <DrawerClose asChild>
                      <Button variant="outline">Close</Button>
                    </DrawerClose>
                  </DrawerFooter>
                </DrawerContent>
              </Drawer>

              {/* Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline">Dropdown ▾</Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuLabel>My Account</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>Profile</DropdownMenuItem>
                  <DropdownMenuItem>Settings</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-destructive">Log out</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Popover */}
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline">Popover</Button>
                </PopoverTrigger>
                <PopoverContent className="w-64">
                  <p className="text-sm">Popover content. Anchored to the trigger element.</p>
                </PopoverContent>
              </Popover>

              {/* Tooltip */}
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button variant="outline">Tooltip</Button>
                </TooltipTrigger>
                <TooltipContent>This is a tooltip</TooltipContent>
              </Tooltip>

              {/* Hover Card */}
              <HoverCard>
                <HoverCardTrigger asChild>
                  <Button variant="outline">Hover Card</Button>
                </HoverCardTrigger>
                <HoverCardContent>
                  <div className="space-y-1">
                    <h4 className="text-sm font-semibold">@demo_user</h4>
                    <p className="text-sm text-muted-foreground">
                      Full-stack developer. Building great things.
                    </p>
                    <p className="text-xs text-muted-foreground">Joined April 2024</p>
                  </div>
                </HoverCardContent>
              </HoverCard>
            </div>
          </Section>

          {/* ── CONTEXT MENU ────────────────────────────────────────────────── */}
          <Section title="Context Menu (right-click)">
            <ContextMenu>
              <ContextMenuTrigger>
                <div className="border-2 border-dashed rounded-md p-8 text-center text-sm text-muted-foreground select-none cursor-context-menu">
                  Right-click anywhere in this area
                </div>
              </ContextMenuTrigger>
              <ContextMenuContent>
                <ContextMenuLabel>Actions</ContextMenuLabel>
                <ContextMenuSeparator />
                <ContextMenuItem>View</ContextMenuItem>
                <ContextMenuItem>Edit</ContextMenuItem>
                <ContextMenuItem>Duplicate</ContextMenuItem>
                <ContextMenuSeparator />
                <ContextMenuItem variant="destructive">Delete</ContextMenuItem>
              </ContextMenuContent>
            </ContextMenu>
          </Section>

          {/* ── TOAST ───────────────────────────────────────────────────────── */}
          <Section title="Toast (Sonner)">
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" onClick={() => toast('Default toast')}>Default</Button>
              <Button variant="outline" onClick={() => toast.success('Action completed!')}>Success</Button>
              <Button variant="outline" onClick={() => toast.error('Something went wrong.')}>Error</Button>
              <Button
                variant="outline"
                onClick={() => toast.promise(new Promise((r) => setTimeout(r, 2000)), {
                  loading: 'Loading…',
                  success: 'Done!',
                  error: 'Failed',
                })}
              >
                Promise
              </Button>
            </div>
          </Section>

          {/* ── SEPARATOR ───────────────────────────────────────────────────── */}
          <Section title="Separator">
            <div className="space-y-4">
              <Separator />
              <div className="flex items-center gap-4">
                <span className="text-sm">Left</span>
                <Separator orientation="vertical" className="h-4" />
                <span className="text-sm">Right</span>
              </div>
            </div>
          </Section>
        </div>
      </div>
    </TooltipProvider>
  )
}
