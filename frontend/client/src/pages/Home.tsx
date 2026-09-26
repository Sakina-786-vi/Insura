import { useEffect, useRef, useState, type MouseEvent, type ReactNode } from "react";
import {
  Activity,
  ArrowLeft,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  BadgeCheck,
  Bell,
  BookOpen,
  BrainCircuit,
  Calculator,
  CalendarClock,
  CarFront,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  ClipboardCheck,
  ClipboardList,
  Clock3,
  FileCheck2,
  FileText,
  Flame,
  FolderOpen,
  Gauge,
  HeartPulse,
  House,
  Eye,
  EyeOff,
  KeyRound,
  Lock,
  Menu,
  MessageCircle,
  MoreHorizontal,
  Play,
  QrCode,
  ScanLine,
  Settings2,
  ShieldAlert,
  ShieldCheck,
  Siren,
  Sparkles,
  Stethoscope,
  Target,
  Timer,
  Trophy,
  UploadCloud,
  UserRound,
  Users,
  X,
  Zap,
} from "lucide-react";
import SimulationView from "../components/SimulationView";
import PolicyAssistantView from "../components/PolicyAssistantView";

type View = "home" | "learn" | "compare" | "simulate" | "passport" | "rewards" | "reminders" | "claims" | "documents" | "assistant" | "profile" | "settings" | "help";
type AuthMode = "signin" | "register";
type IconType = typeof House;

const iconMap: Record<string, IconType> = {
  home: House,
  learn: BookOpen,
  simulate: Activity,
  passport: ShieldCheck,
  rewards: Trophy,
};

function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <span className="logo-mark" aria-hidden="true">
        <ShieldCheck size={20} strokeWidth={1.7} />
      </span>
      {!compact && (
        <span className="font-display text-[15px] font-semibold tracking-[.18em] text-white">
          INSURA
        </span>
      )}
    </div>
  );
}

function ProtectionScene({ small = false }: { small?: boolean }) {
  return (
    <div className={`protection-scene ${small ? "scale-[.75] origin-center" : ""}`} aria-label="Abstract INSURA protection scene">
      <div className="scene-grid" />
      <div className="ambient-orb one" style={{ left: "19%", top: "25%" }} />
      <div className="ambient-orb two" style={{ right: "15%", top: "18%" }} />
      <div className="ambient-orb three" style={{ left: "12%", bottom: "22%" }} />
      <div className="orbit orbit-a" />
      <div className="orbit orbit-b" />
      <div className="scene-ring" />
      <div className="scene-shield" />
      <div className="scene-doc"><div className="doc-head" /></div>
      <div className="float-chip chip-a"><ScanLine size={13} /> policy scan</div>
      <div className="float-chip chip-b"><BadgeCheck size={13} /> 82% ready</div>
      <div className="float-chip chip-c"><Lock size={13} /> protected</div>
      <span className="scene-label policy">policy</span>
      <span className="scene-label ai">ai understanding</span>
      <span className="scene-label ready">passport ready</span>
    </div>
  );
}

function AmbientDots() {
  return (
    <>
      <span className="ambient-orb one" style={{ left: "7%", top: "22%" }} />
      <span className="ambient-orb two" style={{ left: "44%", top: "12%" }} />
      <span className="ambient-orb three" style={{ left: "82%", top: "30%" }} />
      <span className="ambient-orb two" style={{ left: "72%", top: "73%" }} />
      <span className="ambient-orb three" style={{ left: "18%", top: "84%" }} />
    </>
  );
}

function Landing({ onStart, onAuth, authenticated = false, userName = 'Riya' }: { onStart: () => void; onAuth: (mode: AuthMode) => void; authenticated?: boolean; userName?: string }) {
  const [step, setStep] = useState(0);
  const [coreOffset, setCoreOffset] = useState({ x: 0, y: 0 });
  const journey = ['Understand', 'Learn', 'Simulate', 'Remember', 'Be prepared'];
  useEffect(() => { const timer = window.setInterval(() => setStep((value) => (value + 1) % journey.length), 2400); return () => window.clearInterval(timer); }, []);
  const onMove = (event: MouseEvent<HTMLElement>) => { const rect = event.currentTarget.getBoundingClientRect(); setCoreOffset({ x: (event.clientX - rect.left - rect.width / 2) / 38, y: (event.clientY - rect.top - rect.height / 2) / 52 }); };
  return <div className="app-shell landing-shell min-h-screen" onMouseMove={onMove}>
    <AmbientDots /><div className="hero-grid pointer-events-none absolute inset-0 opacity-50" />
    <header className="landing-nav glass-soft relative z-10 mx-auto mt-4 flex w-[calc(100%-28px)] max-w-[1180px] items-center justify-between rounded-full px-4 py-2.5 lg:px-5">
      <button className="border-0 bg-transparent p-0" onClick={onStart} aria-label="Open INSURA"><Logo /></button>
      <nav className="hidden items-center gap-7 md:flex">{['How it works', 'Learning', 'Simulator', 'Security'].map((item) => <button key={item} onClick={() => document.getElementById('product-story')?.scrollIntoView({ behavior: 'smooth' })} className="border-0 bg-transparent text-[11px] text-[#8598b9] transition hover:text-white">{item}</button>)}</nav>
      {!authenticated ? <div className="flex items-center gap-2"><button className="btn btn-ghost rounded-full px-3.5 py-2 text-[11px]" onClick={() => onAuth('signin')}>Sign in</button><button className="btn btn-primary rounded-full px-3.5 py-2 text-[11px] font-bold" onClick={() => onAuth('register')}>Register <ArrowUpRight size={13} className="ml-1 inline" /></button></div> : <div className="flex items-center gap-2"><span className="rounded-full border border-[#8eb9f322] bg-[#13203a99] px-3 py-1.5 text-[10px] uppercase tracking-[0.18em] text-[#a2dfff]">Signed in as {userName}</span></div>}
    </header>
    <main className="relative z-10 mx-auto max-w-[1220px] px-5 pb-20 lg:px-8">
      <section className="center-hero">
        <div className="center-hero-copy"><span className="label-caps">Insurance, made legible</span><h1 className="mt-3 font-display text-[clamp(30px,3.4vw,42px)] font-semibold leading-[1.04] tracking-[-.055em]">Insurance, finally <span className="text-gradient">understandable.</span></h1><p className="mx-auto mt-3 max-w-[430px] text-[13px] leading-6 text-[#8c9dba]">INSURA turns your policy into an interactive journey — from complex clauses to confident next steps.</p></div>
        <div className="center-stage-grid">
          <aside className="policy-stream"><span className="label-caps">Your policy</span><div className="stream-line" />{[{ value: '₹10,00,000', label: 'Coverage' }, { value: '14 Aug 2026', label: 'Valid until' }, { value: '₹12,000', label: 'Annual premium' }].map(({ value, label }, i) => <div key={label} className={`stream-card ${step === i ? 'active' : ''}`}><span className="stream-pulse" /><div><strong>{value}</strong><small>{label}</small></div><Check size={13} /></div>)}</aside>
          <div className="core-stage" style={{ transform: `translate3d(${coreOffset.x}px, ${coreOffset.y}px, 0)` }}><div className="core-caption"><span className="core-dot" /> Insurance core <span className="font-mono text-[#6f85aa]">/ live</span></div><ProtectionScene /><div className="core-flow"><span>complex policy</span><ArrowRight size={12} /><span>understood</span><ArrowRight size={12} /><span>prepared</span></div></div>
          <aside className="journey-stream"><span className="label-caps">Your journey</span><div className="journey-list">{journey.map((item, i) => <div key={item} className={`journey-step ${i === step ? 'active' : ''} ${i < step ? 'done' : ''}`}><span>{i < step ? <Check size={11} /> : String(i + 1).padStart(2, '0')}</span><strong>{item}</strong>{i < journey.length - 1 && <i />}</div>)}</div></aside>
        </div>
        <div className="center-cta"><button className="btn btn-primary rounded-full px-5 py-3 text-[12px] font-bold" onClick={onStart}>{authenticated ? 'Continue my insurance journey' : 'Start my insurance journey'} <ArrowRight size={14} className="ml-1.5 inline" /></button><button className="btn btn-ghost rounded-full px-5 py-3 text-[12px]" onClick={() => document.getElementById('product-story')?.scrollIntoView({ behavior: 'smooth' })}>Explore INSURA <ArrowDownRight size={14} className="ml-1 inline" /></button></div>
      </section>
      <section id="product-story" className="product-story border-t border-[#8aaef012] py-20"><div className="story-heading"><div><span className="label-caps">One policy. One journey.</span><h2 className="mt-3 font-display text-[clamp(24px,3vw,36px)] font-semibold tracking-[-.055em]">From upload to <span className="text-gradient">prepared.</span></h2></div><p>Every step has a purpose. Watch your policy become something you can actually use.</p></div><div className="story-layout"><div className="story-rail">{['Upload', 'Understand', 'Learn', 'Simulate', 'Prepare'].map((item, i) => <button key={item} onClick={() => setStep(i)} className={`story-step ${step === i ? 'active' : ''}`}><span>{String(i + 1).padStart(2, '0')}</span><strong>{item}</strong><small>{['Bring in the fine print', 'Find what matters', 'Build confidence', 'Rehearse the what-if', 'Keep it close'][i]}</small></button>)}</div><div className="story-preview glass"><div className="preview-top"><span className="label-caps">Live product preview</span><span className="status-dot teal">{step < 4 ? 'Processing' : 'Ready'}</span></div><div className={`preview-art stage-${step}`}><div className="preview-doc"><FileText size={22} /><span /><span /><span /></div><div className="preview-shield"><ShieldCheck size={28} /></div><div className="preview-node node-a"><ScanLine size={14} /></div><div className="preview-node node-b"><HeartPulse size={14} /></div><div className="preview-node node-c"><Bell size={14} /></div></div><div className="preview-copy"><span className="label-caps">Step {String(step + 1).padStart(2, '0')} / 05</span><h3>{['Policy uploaded', 'Coverage extracted', 'Learning level generated', 'Situation simulated', 'Insurance Passport ready'][step]}</h3><p>{['Your document is safely inside the INSURA flow.', 'Important limits and dates are being structured.', 'A personal learning path is shaped around your cover.', 'You know the next action before the real moment arrives.', 'Your policy, progress, and reminders are now in one place.'][step]}</p></div></div></div></section>
      <section className="mini-product-section"><div className="story-heading"><div><span className="label-caps">See what INSURA does</span><h2 className="mt-3 font-display text-[clamp(24px,3vw,34px)] font-semibold tracking-[-.05em]">A calmer command center.</h2></div><p>Not another dashboard. A focused place to learn, simulate, and prepare.</p></div><div className="mini-dashboard glass"><div className="mini-sidebar"><Logo compact /><span className="mini-active"><House size={13} /> Home</span><span><BookOpen size={13} /> Learn</span><span><Activity size={13} /> Simulate</span><span><ShieldCheck size={13} /> Passport</span></div><div className="mini-main"><div className="mini-header"><span className="label-caps">Good evening, Riya</span><span className="status-dot teal">Policy active</span></div><div className="mini-cards"><div className="mini-card emphasis"><span className="label-caps">Learning progress</span><strong>68%</strong><div className="progress-track"><span style={{ width: '68%' }} /></div></div><div className="mini-card"><span className="label-caps">Important clause</span><strong>₹10k deductible</strong><small>Policy Document · Page 4</small></div><div className="mini-card"><span className="label-caps">Reminder created</span><strong>Premium due</strong><small>In 7 days</small></div></div><div className="mini-timeline"><span className="done"><Check size={12} /></span><i /><span className="done"><Check size={12} /></span><i /><span className="active"><Sparkles size={12} /></span><i /><span><Lock size={12} /></span></div><div className="mini-timeline-labels"><span>Uploaded</span><span>Understood</span><span>Learning level</span><span>Prepared</span></div></div></div></section>
    </main>
    <footer className="relative z-10 mx-auto flex max-w-[1220px] items-center justify-between border-t border-[#8aaef012] px-5 py-6 text-[10px] text-[#627596] lg:px-8"><span>© 2026 INSURA</span><span>Understand. Learn. Stay Protected.</span></footer>
  </div>;
}
function TopBar({ active, onBrand, onProfile, userName }: { active: View; onBrand: () => void; onProfile: () => void; userName: string }) {
  const titles: Record<View, string> = {
    home: 'Command center', learn: 'Learning path', compare: 'Policy comparison', simulate: 'Situation simulator', passport: 'Insurance passport', rewards: 'Rewards', reminders: 'Reminders', claims: 'Claim journey', documents: 'Document center', assistant: 'Policy assistant', profile: 'Profile', settings: 'Settings', help: 'Help & support',
  };
  const initials = userName.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase() || 'U';
  return (
    <div className="app-topbar">
      <button onClick={onBrand} className="border-0 bg-transparent p-0"><Logo /></button>
      <div className="topbar-copy breadcrumb"><span>Workspace</span><ChevronRight size={13} /><strong>{titles[active]}</strong></div>
      <div className="flex items-center gap-3">
        <button onClick={onProfile} className="relative grid h-9 w-9 place-items-center rounded-full border border-[#8eb9f322] bg-[#13203a99] text-[#8fa4c8] transition hover:border-[#67ddff66] hover:text-[#bdf5ff]" aria-label="Open notifications"><Bell size={15} /><span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-[#64e3b2] shadow-[0_0_8px_#64e3b2]" /></button>
        <button onClick={onProfile} className="profile-chip"><span className="avatar">{initials.slice(0, 1)}</span><span className="hidden text-[11px] font-medium text-[#dceaff] sm:inline">{userName}</span><ChevronRight size={13} className="text-[#7185a5]" /></button>
      </div>
    </div>
  );
}
function CommandDock({ active, setActive, moreOpen, setMoreOpen }: { active: View; setActive: (view: View) => void; moreOpen: boolean; setMoreOpen: (open: boolean) => void }) {
  const items: { key: View; label: string; icon: IconType }[] = [
    { key: 'home', label: 'Home', icon: House }, { key: 'learn', label: 'Learn', icon: BookOpen }, { key: 'simulate', label: 'Simulate', icon: Activity }, { key: 'passport', label: 'Passport', icon: ShieldCheck }, { key: 'rewards', label: 'Rewards', icon: Trophy },
  ];
  const extras: { key: View; label: string; detail: string; status?: string; icon: IconType }[] = [
    { key: 'reminders', label: 'Reminders', detail: 'Premium, renewal & important dates', status: '3 upcoming', icon: CalendarClock },
    { key: 'compare', label: 'Compare policies', detail: 'See what changed at renewal', icon: FileCheck2 },
    { key: 'claims', label: 'Claims', detail: 'Track your claim journey', status: 'No active claim', icon: ClipboardList },
    { key: 'documents', label: 'Documents', detail: 'Policy and supporting documents', status: '2 documents', icon: FolderOpen },
    { key: 'assistant', label: 'AI Assistant', detail: 'Ask questions about your policy', icon: MessageCircle },
    { key: 'profile', label: 'Profile', detail: 'Personal information & passport', icon: UserRound },
    { key: 'settings', label: 'Settings', detail: 'Notifications, privacy & preferences', icon: Settings2 },
    { key: 'help', label: 'Help & support', detail: 'Get assistance', icon: CircleHelp },
  ];
  return <div className="dock-wrap"><div className="relative">
    {moreOpen && <div className="more-menu glass"><div className="more-menu-head"><span className="label-caps">Command panel</span><button onClick={() => setMoreOpen(false)} aria-label="Close more"><X size={14} /></button></div>{extras.map(({ key, label, detail, status, icon: Icon }) => <button key={key} onClick={() => { setActive(key); setMoreOpen(false); }}><span className="more-icon"><Icon size={15} /></span><span><strong>{label}</strong><small>{detail}</small>{status && <em>{status}</em>}</span><ChevronRight size={13} className="more-arrow" /></button>)}</div>}
    <div className="command-dock">{items.map(({ key, label, icon: Icon }, i) => <>{i === 2 && <button key="brand" className="dock-center" aria-label="INSURA home" onClick={() => { setActive('home'); setMoreOpen(false); }}><span className="logo-mark"><ShieldCheck size={19} strokeWidth={1.7} /></span></button>}<button key={key} onClick={() => { setActive(key); setMoreOpen(false); }} className={`dock-item ${active === key ? 'active' : ''}`}><Icon size={16} />{label}</button></>)}<button aria-label="More options" onClick={() => setMoreOpen(!moreOpen)} className={`dock-item ${moreOpen ? 'active' : ''}`}><MoreHorizontal size={17} />More</button></div>
  </div></div>;
}
type PolicyOutput = {
  document?: { insurer?: string | null; product_name?: string | null; uin?: string | null; document_type?: string | null } | null;
  coverage?: { sum_insured_options?: string[]; hospitalization?: boolean | null; day_care?: boolean | null; domiciliary?: boolean | null; ambulance?: string | null; health_checkup?: string | null } | null;
  financial?: { premium_tables?: Array<Record<string, unknown>>; deductible?: string | null; copayment?: string | null } | null;
  limits?: { room_rent?: string | null; icu?: string | null; cataract?: string | null; major_surgeries?: string | null } | null;
  waiting_periods?: Array<{ condition?: string | null; period?: string | null }>;
  exclusions?: string[];
  claim_process?: { cashless?: string[]; reimbursement?: string[]; documents?: string[]; deadlines?: string[] } | null;
  renewal?: { renewable?: boolean | null; conditions?: string[] } | null;
  important_conditions?: string[];
  source_evidence?: Array<Record<string, unknown>>;
};

const policyValue = (value: unknown) => value === null || value === undefined || value === '' ? 'Not specified in the document' : String(value);

function getPolicySimulationScenarios(policy: PolicyOutput | null) {
  if (!policy) return [];
  const scenarios: string[] = [];
  const coverage = policy.coverage;
  const financial = policy.financial;
  const limits = policy.limits;
  if (coverage?.hospitalization === true) scenarios.push('What if you are admitted to hospital for a covered treatment?');
  if (limits?.icu) scenarios.push(`What if you need ICU care and the daily charge is above ${limits.icu}?`);
  if (financial?.deductible) scenarios.push(`What if you submit an eligible claim with a ${financial.deductible} deductible?`);
  if (financial?.copayment) scenarios.push(`What if your eligible claim includes a ${financial.copayment} co-payment?`);
  if (policy.waiting_periods?.length) scenarios.push('What if your treatment falls within one of the listed waiting periods?');
  if (policy.claim_process?.cashless?.length) scenarios.push('What if you use a network hospital and request a cashless claim?');
  if (policy.claim_process?.reimbursement?.length) scenarios.push('What if you pay the hospital first and request reimbursement?');
  if (coverage?.domiciliary === false) scenarios.push('What if you need domiciliary treatment instead of hospital admission?');
  return scenarios;
}

function PolicySnapshot({ policy }: { policy: PolicyOutput | null }) {
  const document = policy?.document;
  const coverage = policy?.coverage;
  return <section className="glass card-hover rounded-[22px] p-5"><div className="flex items-center justify-between"><div><span className="label-caps">Policy snapshot</span><h3 className="mt-2 font-display text-[18px] font-semibold tracking-[-.03em]">{policyValue(document?.product_name)}</h3></div><span className="rounded-full border border-[#6de0ba44] bg-[#6de0ba12] px-2 py-1 text-[9px] text-[#82e7bd]">ANALYZED</span></div><div className="mt-5 grid grid-cols-2 gap-y-4"><div><span className="label-caps">Insurer</span><b className="mt-1 block text-[13px]">{policyValue(document?.insurer)}</b></div><div><span className="label-caps">UIN</span><b className="mt-1 block text-[13px]">{policyValue(document?.uin)}</b></div><div><span className="label-caps">Document type</span><b className="mt-1 block text-[13px]">{policyValue(document?.document_type)}</b></div><div><span className="label-caps">Hospitalization</span><b className="mt-1 block text-[13px]">{coverage?.hospitalization === null || coverage?.hospitalization === undefined ? 'Not specified in the document' : coverage.hospitalization ? 'Covered' : 'Not covered'}</b></div><div><span className="label-caps">Sum insured options</span><b className="mt-1 block text-[13px]">{policyValue(coverage?.sum_insured_options?.join(', '))}</b></div><div><span className="label-caps">Copayment</span><b className="mt-1 block text-[13px]">{policyValue(policy?.financial?.copayment)}</b></div></div><button className="btn btn-ghost mt-5 w-full rounded-xl py-2.5 text-[11px]">Policy intelligence loaded</button></section>;
}

type ProgressionData = {
  xp: number;
  streak: number;
  readiness: number;
  completed_levels: number;
  total_levels: number;
  learning_percentage: number;
  level: number;
  next_milestone_xp: number;
  badges?: Array<{ name?: string; description?: string }>;
  completed_learning_items?: string[];
};

function HomeView({ xp, streak, progress, onToast, onLesson, onSimulation, userName, policy, learning }: { xp: number; streak: number; progress: ProgressionData; onToast: (message: string) => void; onLesson: () => void; onSimulation: (scenario: string) => void; userName: string; policy: PolicyOutput | null; learning: LearningData | null }) {
  const [simulationScenario, setSimulationScenario] = useState('');
  const readiness = Math.max(0, Math.min(100, Number(progress?.readiness ?? 0)));
  const learningPercentage = Math.max(0, Math.min(100, Number(progress?.learning_percentage ?? 0)));
  const nextMilestone = Math.max(0, Number(progress?.next_milestone_xp ?? 0));
  const nextConcept = getNextLearningConcept(learning, progress.completed_learning_items);
  useEffect(() => {
    const scenarios = getPolicySimulationScenarios(policy);
    setSimulationScenario(scenarios.length ? scenarios[Math.floor(Math.random() * scenarios.length)] : '');
  }, [policy]);
  return <div className="dashboard-grid">
    <div className="grid gap-[18px]">
      <section className="glass hero-dashboard rounded-[24px]">
        <div className="scanline" />
        <span className="label-caps">Wednesday · 23 September 2026</span>
        <div className="relative z-[1] mt-4 max-w-[480px]"><h1>Good evening, {userName.split(' ')[0]}.</h1><p className="mt-3 max-w-[370px] text-[13px] leading-6 text-[#91a2bf]">Your insurance journey is <strong className="text-[#d9f8ff]">{learningPercentage}% complete</strong>. One small lesson today keeps future-you calm.</p></div>
        <div className="metric-row max-w-[530px]"><div className="metric"><span>Insurance readiness</span><b>{readiness}<span className="text-[13px] text-[#6f8aa9]"> / 100</span></b></div><div className="metric"><span>Learning progress</span><b>{learningPercentage}<span className="text-[13px] text-[#6f8aa9]">%</span></b></div><div className="metric"><span>Next milestone</span><b className="text-[#73e4bc]">+{nextMilestone} <span className="text-[13px] text-[#6f8aa9]">XP</span></b></div></div>
      </section>
      <div className="grid gap-[18px] md:grid-cols-[1.05fr_.95fr]">
        <section className="glass lesson-card card-hover rounded-[22px]"><div className="flex items-start justify-between"><div><span className="label-caps">Continue your journey</span><h2 className="mt-3 font-display text-[22px] font-semibold tracking-[-.04em]">{nextConcept ? fieldText(nextConcept.concept, ['concept_name', 'title', 'name'], `Concept ${nextConcept.index + 1}`) : 'Learning path complete'}</h2><p className="mt-2 text-[12px] text-[#8395b5]">{nextConcept ? fieldText(nextConcept.concept, ['explanation', 'description', 'policy_reference', 'content', 'body'], 'Continue with this saved policy concept.') : 'You have completed the available concepts.'}</p></div><span className="lesson-icon"><Calculator size={20} /></span></div><div className="mt-6 flex items-center gap-3"><div className="progress-track flex-1"><span style={{ width: `${Math.min(100, learningPercentage)}%` }} /></div><span className="font-mono text-[10px] text-[#79dfff]">{Math.min(progress.completed_levels || 0, progress.total_levels || 5)} / {progress.total_levels || 5}</span></div><div className="mt-5 flex items-center justify-between"><span className="text-[11px] text-[#8799b9]"><Zap size={13} className="mr-1 inline text-[#f1ca74]" /> Saved learning path</span><button type="button" disabled={!nextConcept} onClick={onLesson} className="btn btn-primary rounded-full px-4 py-2 text-[11px] font-bold disabled:opacity-50">Click to Learn <ArrowRight size={13} className="ml-1 inline" /></button></div></section>
        <section className="glass story-card card-hover rounded-[22px]"><div className="flex items-center justify-between"><span className="story-index"><Sparkles size={12} /> SIMULATION</span><span className="font-mono text-[10px] text-[#768bae]">Policy based</span></div><h3 className="mt-5 font-display text-[18px] font-semibold tracking-[-.03em]">{simulationScenario || 'Upload a policy to create a simulation.'}</h3><p className="mt-2 text-[12px] leading-5 text-[#a4b4cf]">Explore what your stored policy says could happen in this situation.</p><button disabled={!simulationScenario} onClick={() => onSimulation(simulationScenario)} className="btn btn-primary mt-4 rounded-full px-4 py-2 text-[11px] font-bold disabled:opacity-50">See what happens <ArrowRight size={13} className="ml-1 inline" /></button></section>
      </div>
    </div>
    <div className="right-stack">
      <section className="glass score-card rounded-[22px]"><div className="section-title"><div><span className="label-caps">Preparedness, not a policy score</span><h2 className="mt-2">Readiness</h2></div><Gauge size={17} className="text-[#70ddff]" /></div><div className="score-ring" style={{ background: `conic-gradient(#5bdfff 0 ${readiness}%, rgba(101,129,189,.12) ${readiness}% 100%)` }}><div><b>{readiness}</b><span>of 100</span></div></div><div className="score-check"><span>Policy understood</span><Check size={14} /></div><div className="score-check"><span>Coverage understood</span><Check size={14} /></div><div className="score-check"><span>Important clauses</span><span className="text-[#f0c66c]">review</span></div></section>
      <div className="side-metrics"><section className="glass side-metric rounded-[18px]"><div className="flex items-start justify-between"><span className="label-caps">Streak</span><Flame className="flame text-[#ffb24e]" /></div><div className="mt-3 xp-num">{streak} <span className="text-[11px] font-normal text-[#8093b6]">days</span></div><p className="mt-1 text-[10px] text-[#7d90b0]">Best: 21 days</p></section><section className="glass side-metric rounded-[18px]"><div className="flex items-start justify-between"><span className="label-caps">Insurance XP</span><Zap size={17} className="text-[#f1cc75]" /></div><div className="mt-3 xp-num">{xp.toLocaleString()}</div><p className="mt-1 text-[10px] text-[#7d90b0]">+{nextMilestone} to next milestone</p></section></div>
      <PolicySnapshot policy={policy} />
    </div>
  </div>;
}

type LearningPackage = {
  concepts?: Array<Record<string, any>>;
  scenarios?: Array<Record<string, any>>;
  mcqs?: Array<Record<string, any>>;
};

type LearningData = { learning_package?: LearningPackage; total_concepts?: number; total_scenarios?: number; total_mcqs?: number };

const displayValue = (value: unknown) => typeof value === 'string' ? value : value == null ? '' : JSON.stringify(value);
const fieldText = (item: Record<string, unknown>, keys: string[], fallback: string) => {
  for (const key of keys) {
    const value = displayValue(item[key]);
    if (value) return value;
  }
  return fallback;
};

const getNextLearningConcept = (learning: LearningData | null, completedItems: string[] = []) => {
  const concepts = learning?.learning_package?.concepts || [];
  return concepts.map((concept, index) => ({ concept, index })).find(({ concept, index }) => {
    const title = fieldText(concept, ['concept_name', 'title', 'name'], `Concept ${index + 1}`);
    return !completedItems.some((key) => key === `learning:concept:${index}:${title}` || key.startsWith(`learning:concept:${index}:`));
  }) || null;
};

async function awardLearningXP(activityType: string, activityId: string) {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const response = await fetch(`${API_BASE}/api/progression`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ activity_type: activityType, activity_id: activityId }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || 'XP could not be saved.');
  if (data.progress) window.dispatchEvent(new CustomEvent('insura:progress-updated', { detail: data.progress }));
  return data;
}

function ScenarioExperience({ scenarios, completedLearningItems = [], onToast }: { scenarios: Array<Record<string, any>>; completedLearningItems?: string[]; onToast: (message: string) => void }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [revealed, setRevealed] = useState<Record<number, boolean>>({});
  const [serverCompletedItems, setServerCompletedItems] = useState<string[]>([]);
  const persistedItems = completedLearningItems.length ? completedLearningItems : serverCompletedItems;
  useEffect(() => {
    const loadProgress = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || window.location.origin}/api/progression`, { credentials: 'include' });
        const data = await response.json().catch(() => ({}));
        if (response.ok && Array.isArray(data.progress?.completed_learning_items)) setServerCompletedItems(data.progress.completed_learning_items);
      } catch {
        // Keep the scenario view usable if the refresh is unavailable.
      }
    };
    void loadProgress();
  }, []);
  useEffect(() => {
    setRevealed((current) => ({
      ...current,
      ...Object.fromEntries(scenarios.map((item, index) => [`${index}`, persistedItems.some((key) => key.startsWith(`learning:scenario:${index}:`))])),
    }));
  }, [scenarios, persistedItems.join('|')]);
  if (scenarios.length === 0) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">No scenarios are available for this learning path yet.</section>;
  const current = scenarios[currentIndex];
  const isRevealed = Boolean(revealed[currentIndex]);
  const reveal = async () => {
    if (isRevealed) return;
    setRevealed((items) => ({ ...items, [currentIndex]: true }));
    try {
      await awardLearningXP('learning_scenario', `learning:scenario:${currentIndex}:${fieldText(current, ['scenario', 'scenario_title', 'title'], String(currentIndex))}`);
      onToast(`Scenario ${currentIndex + 1} completed`);
    } catch {
      onToast('Guidance revealed, but scenario progress could not be saved.');
    }
  };
  const completed = Object.values(revealed).filter(Boolean).length;
  return <section className="glass mt-5 rounded-[22px] p-5"><div className="section-title"><div><span className="label-caps">Apply what you know</span><h2 className="mt-2 font-display text-[22px] font-semibold">Real-life scenarios</h2><p>Think through the situation, then reveal the policy-grounded next step.</p></div><span className="status-dot teal">{completed} / {scenarios.length} complete</span></div><div className="unit-tabs mb-5">{scenarios.map((scenario, index) => <button key={`scenario-tab-${index}`} onClick={() => setCurrentIndex(index)} className={`unit-tab ${index === currentIndex ? 'active' : ''}`}>Scenario {index + 1}</button>)}</div><article className="glass-soft rounded-[20px] p-5"><span className="label-caps">Scenario {currentIndex + 1} · {fieldText(current, ['concept_name'], 'Policy decision')}</span><h3 className="mt-3 font-display text-[20px] font-semibold">{fieldText(current, ['scenario'], `Scenario ${currentIndex + 1}`)}</h3><div className="mt-5 rounded-[15px] border border-[#8ab3ea18] bg-[#0a1328a6] p-4"><span className="label-caps">What would you do?</span><p className="mt-2 text-[12px] leading-5 text-[#b7c9e3]">Think about the next action that best follows your policy before revealing the guidance.</p></div>{!isRevealed ? <button onClick={reveal} className="btn btn-primary mt-5 rounded-full px-4 py-2.5 text-[11px] font-bold">Reveal policy guidance <ArrowRight size={13} className="ml-1 inline" /></button> : <div className="mt-5 rounded-[15px] border border-[#67dfb533] bg-[#4ed59e0e] p-4 text-[12px] leading-5 text-[#9beacd]"><strong className="block">Scenario completed</strong><p className="mt-2"><span className="label-caps">Recommended action</span><br />{fieldText(current, ['recommended_action'], 'No recommended action was provided.')}</p><p className="mt-3"><span className="label-caps">What to understand</span><br />{fieldText(current, ['what_to_understand'], 'No additional explanation was provided.')}</p></div>}<div className="mt-5 flex items-center justify-between"><button disabled={currentIndex === 0} onClick={() => setCurrentIndex((index) => index - 1)} className="btn btn-ghost rounded-full px-3 py-2 text-[11px] disabled:opacity-40">Previous</button><span className="font-mono text-[10px] text-[#8194b4]">{currentIndex + 1} / {scenarios.length}</span><button disabled={currentIndex === scenarios.length - 1} onClick={() => setCurrentIndex((index) => index + 1)} className="btn btn-ghost rounded-full px-3 py-2 text-[11px] disabled:opacity-40">Next</button></div></article></section>;
}

function LearnView({ learning, completedLearningItems = [], loading, generating, canGenerate, error, onGenerate, onToast }: { learning: LearningData | null; completedLearningItems?: string[]; loading: boolean; generating: boolean; canGenerate: boolean; error: string; onGenerate: () => void; onToast: (message: string) => void }) {
  const packageData = learning?.learning_package;
  const concepts = packageData?.concepts || [];
  const scenarios = packageData?.scenarios || [];
  const mcqs = packageData?.mcqs || [];
  const [activeConceptIndex, setActiveConceptIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [serverCompletedItems, setServerCompletedItems] = useState<string[]>([]);
  const conceptRefs = useRef<Array<HTMLElement | null>>([]);
  const persistedItems = completedLearningItems.length ? completedLearningItems : serverCompletedItems;
  useEffect(() => {
    const loadProgress = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || window.location.origin}/api/progression`, { credentials: 'include' });
        const data = await response.json().catch(() => ({}));
        if (response.ok && Array.isArray(data.progress?.completed_learning_items)) setServerCompletedItems(data.progress.completed_learning_items);
      } catch {
        // Keep the learning page usable if the refresh is unavailable.
      }
    };
    void loadProgress();
  }, []);
  useEffect(() => {
    const restored = Object.fromEntries(mcqs.map((mcq, index) => {
      const key = `learning:question:${index}:${fieldText(mcq, ['question', 'prompt'], String(index))}`;
      return persistedItems.includes(key) ? [index, displayValue(mcq.correct_answer)] : null;
    }).filter(Boolean) as Array<[number, string]>);
    setAnswers((current) => ({ ...restored, ...current }));
  }, [learning, persistedItems.join('|')]);
  const selectConcept = (index: number) => { setActiveConceptIndex(index); conceptRefs.current[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' }); };
  const selectAnswer = async (index: number, option: unknown) => {
    if (answers[index] !== undefined) return;
    const mcq = mcqs[index] || {};
    const selected = displayValue(option);
    const correct = displayValue(mcq.correct_answer);
    const options = Array.isArray(mcq.options) ? mcq.options.map(displayValue) : [];
    const correctIndex = options.findIndex((item) => item === correct);
    const selectedIndex = options.findIndex((item) => item === selected);
    const isCorrect = correct === selected || (correctIndex >= 0 && correctIndex === selectedIndex) || correct === String.fromCharCode(65 + selectedIndex);
    setAnswers((items) => ({ ...items, [index]: selected }));
    try {
      await awardLearningXP(isCorrect ? 'learning_question_correct' : 'learning_question_wrong', `learning:question:${index}:${fieldText(mcq, ['question', 'prompt'], String(index))}`);
      onToast(isCorrect ? '+10 XP · Correct answer' : '-5 XP · Review this answer');
    } catch {
      onToast('Answer selected, but XP could not be saved.');
    }
  };
  const answerResult = (mcq: Record<string, any>, index: number) => { const selected = answers[index]; if (selected === undefined) return null; const correct = displayValue(mcq.correct_answer); const options = Array.isArray(mcq.options) ? mcq.options.map(displayValue) : []; const correctIndex = options.findIndex((option) => option === correct); const selectedIndex = options.findIndex((option) => option === selected); return { isCorrect: correct === selected || (correctIndex >= 0 && correctIndex === selectedIndex) || correct === String.fromCharCode(65 + selectedIndex), correct }; };
  if (loading) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Loading your saved learning…</section>;
  if (generating) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Creating your personalized learning…</section>;
  if (!learning && canGenerate) return <section className="glass rounded-[22px] p-6"><p className="text-[12px] text-[#9bb0d0]">Your policy is ready. Generate a personalized learning path from its saved intelligence.</p><button onClick={onGenerate} className="btn btn-primary mt-4 rounded-full px-4 py-2.5 text-[11px] font-bold">Start Learning <ArrowRight size={13} className="ml-1 inline" /></button></section>;
  if (!learning) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Upload a policy first to start learning.</section>;
  return <div><div className="learn-header"><div><span className="label-caps">Your path to confidence</span><h1 className="mt-2 font-display text-[32px] font-semibold tracking-[-.06em]">Learn your cover.</h1></div><button onClick={() => onToast(`${concepts.length} concepts · ${scenarios.length} scenarios · ${mcqs.length} checks`)} className="btn btn-ghost rounded-full px-4 py-2 text-[11px]"><Timer size={13} className="mr-1 inline" /> {mcqs.length} knowledge checks</button></div>{error && <section className="glass mb-5 rounded-[22px] border border-[#ed778933] p-6 text-[12px] text-[#ffb4bf]">{error}</section>}<div className="unit-tabs mb-5">{concepts.map((concept, index) => <button key={`concept-${index}`} onClick={() => selectConcept(index)} className={`unit-tab ${index === activeConceptIndex ? 'active' : ''}`}>{String(index + 1).padStart(2, '0')} {fieldText(concept, ['concept_name', 'title', 'name'], `Concept ${index + 1}`)}</button>)}</div><section className="grid gap-4 md:grid-cols-2">{concepts.map((concept, index) => <article ref={(element) => { conceptRefs.current[index] = element; }} className={`glass rounded-[22px] p-5 ${index === activeConceptIndex ? 'border-[#72ddff55]' : ''}`} key={`concept-card-${index}`}><span className="label-caps">Concept {index + 1}</span><h2 className="mt-2 font-display text-[19px] font-semibold">{fieldText(concept, ['concept_name', 'title', 'name'], `Concept ${index + 1}`)}</h2><p className="mt-3 text-[12px] leading-5 text-[#9aacc8]">{fieldText(concept, ['explanation', 'description', 'policy_reference', 'content', 'body'], 'This concept is based on your saved policy.')}</p></article>)}</section><ScenarioExperience scenarios={scenarios} onToast={onToast} /><section className="mt-5 grid gap-4">{mcqs.map((mcq, index) => { const result = answerResult(mcq, index); const options = Array.isArray(mcq.options) ? mcq.options : []; return <article className="glass rounded-[22px] p-5" key={`mcq-${index}`}><span className="label-caps">Knowledge check {index + 1}</span><h2 className="mt-2 font-display text-[18px] font-semibold">{fieldText(mcq, ['question', 'prompt'], `Question ${index + 1}`)}</h2><div className="mt-4 grid gap-2">{options.map((option, optionIndex) => <button key={`option-${optionIndex}`} disabled={answers[index] !== undefined} onClick={() => selectAnswer(index, option)} className={`answer !mt-0 ${result && displayValue(option) === answers[index] ? result.isCorrect ? 'correct' : 'wrong' : ''}`}><span className="mr-2 text-[#6f87aa]">{String.fromCharCode(65 + optionIndex)}</span>{displayValue(option)}</button>)}</div>{result && <div className={`mt-4 rounded-[14px] border p-4 text-[11px] leading-5 ${result.isCorrect ? 'border-[#67dfb533] bg-[#4ed59e0e] text-[#9beacd]' : 'border-[#ed778933] bg-[#ed77890c] text-[#ffb4bf]'}`}>{result.isCorrect ? '✓ Correct answer' : `✕ Incorrect answer${result.correct ? ` · Correct answer: ${result.correct}` : ''}`}{displayValue(mcq.explanation) && <p className="mt-2">{displayValue(mcq.explanation)}</p>}</div>}</article>; })}</section></div>;
}

function LegacyScenarioLearnView({ learning, loading, generating, canGenerate, error, onGenerate, onToast }: { learning: LearningData | null; loading: boolean; generating: boolean; canGenerate: boolean; error: string; onGenerate: () => void; onToast: (message: string) => void }) {
  const packageData = learning?.learning_package;
  const concepts = packageData?.concepts || [];
  const scenarios = packageData?.scenarios || [];
  const mcqs = packageData?.mcqs || [];
  const [activeConceptIndex, setActiveConceptIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const conceptRefs = useRef<Array<HTMLElement | null>>([]);
  const selectConcept = (index: number) => {
    setActiveConceptIndex(index);
    conceptRefs.current[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };
  const selectAnswer = (index: number, option: unknown) => {
    if (answers[index] !== undefined) return;
    setAnswers((current) => ({ ...current, [index]: displayValue(option) }));
  };
  const answerResult = (mcq: Record<string, unknown>, index: number) => {
    const selected = answers[index];
    if (selected === undefined) return null;
    const correct = displayValue(mcq.correct_answer);
    const options = Array.isArray(mcq.options) ? mcq.options.map(displayValue) : [];
    const correctIndex = options.findIndex((option) => option === correct);
    const selectedIndex = options.findIndex((option) => option === selected);
    return { isCorrect: correct === selected || (correctIndex >= 0 && correctIndex === selectedIndex) || correct === String.fromCharCode(65 + selectedIndex), correct };
  };
  if (loading) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Loading your saved learning…</section>;
  if (generating) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Creating your personalized learning…</section>;
  if (!learning && canGenerate) return <section className="glass rounded-[22px] p-6"><p className="text-[12px] text-[#9bb0d0]">Your policy is ready. Generate a personalized learning path from its saved intelligence.</p><button onClick={onGenerate} className="btn btn-primary mt-4 rounded-full px-4 py-2.5 text-[11px] font-bold">Start Learning <ArrowRight size={13} className="ml-1 inline" /></button></section>;
  if (!learning) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Upload a policy first to start learning.</section>;
  return <div><div className="learn-header"><div><span className="label-caps">Your path to confidence</span><h1 className="mt-2 font-display text-[32px] font-semibold tracking-[-.06em]">Learn your cover.</h1></div><button onClick={() => onToast(`${concepts.length} concepts · ${scenarios.length} scenarios · ${mcqs.length} checks`)} className="btn btn-ghost rounded-full px-4 py-2 text-[11px]"><Timer size={13} className="mr-1 inline" /> {mcqs.length} knowledge checks</button></div>{error && <section className="glass mb-5 rounded-[22px] border border-[#ed778933] p-6 text-[12px] text-[#ffb4bf]">{error}</section>}<div className="unit-tabs mb-5">{concepts.map((concept, index) => <button key={`concept-${index}`} onClick={() => selectConcept(index)} className={`unit-tab ${index === activeConceptIndex ? 'active' : ''}`}>{String(index + 1).padStart(2, '0')} {fieldText(concept, ['concept_name', 'title', 'name'], `Concept ${index + 1}`)}</button>)}</div><section className="grid gap-4 md:grid-cols-2">{concepts.map((concept, index) => <article ref={(element) => { conceptRefs.current[index] = element; }} className={`glass rounded-[22px] p-5 ${index === activeConceptIndex ? 'border-[#72ddff55]' : ''}`} key={`concept-card-${index}`}><span className="label-caps">Concept {index + 1}</span><h2 className="mt-2 font-display text-[19px] font-semibold">{fieldText(concept, ['concept_name', 'title', 'name'], `Concept ${index + 1}`)}</h2><p className="mt-3 text-[12px] leading-5 text-[#9aacc8]">{fieldText(concept, ['explanation', 'description', 'policy_reference', 'content', 'body'], 'This concept is based on your saved policy.')}</p></article>)}{scenarios.map((scenario, index) => <article className="glass rounded-[22px] p-5" key={`scenario-${index}`}><span className="label-caps">Scenario {index + 1}</span><h2 className="mt-2 font-display text-[19px] font-semibold">{fieldText(scenario, ['scenario_title', 'title', 'name', 'headline'], `Scenario ${index + 1}`)}</h2><p className="mt-3 text-[12px] leading-5 text-[#9aacc8]">{fieldText(scenario, ['scenario_description', 'situation', 'detail', 'explanation', 'recommended_action', 'content', 'body'], 'Review this situation using the coverage in your policy.')}</p></article>)}</section><section className="mt-5 grid gap-4">{mcqs.map((mcq, index) => { const result = answerResult(mcq, index); const options = Array.isArray(mcq.options) ? mcq.options : []; return <article className="glass rounded-[22px] p-5" key={`mcq-${index}`}><span className="label-caps">Knowledge check {index + 1}</span><h2 className="mt-2 font-display text-[18px] font-semibold">{fieldText(mcq, ['question', 'prompt'], `Question ${index + 1}`)}</h2><div className="mt-4 grid gap-2">{options.map((option, optionIndex) => <button key={`option-${optionIndex}`} disabled={answers[index] !== undefined} onClick={() => selectAnswer(index, option)} className={`answer !mt-0 ${result && displayValue(option) === answers[index] ? result.isCorrect ? 'correct' : 'wrong' : ''}`}><span className="mr-2 text-[#6f87aa]">{String.fromCharCode(65 + optionIndex)}</span>{displayValue(option)}</button>)}</div>{result && <div className={`mt-4 rounded-[14px] border p-4 text-[11px] leading-5 ${result.isCorrect ? 'border-[#67dfb533] bg-[#4ed59e0e] text-[#9beacd]' : 'border-[#ed778933] bg-[#ed77890c] text-[#ffb4bf]'}`}>{result.isCorrect ? '✓ Correct answer' : `✕ Incorrect answer${result.correct ? ` · Correct answer: ${result.correct}` : ''}`}{mcq.explanation && <p className="mt-2">{displayValue(mcq.explanation)}</p>}</div>}</article>; })}</section></div>;
}

function LegacyLearnView({ learning, loading, generating, canGenerate, error, onGenerate, onToast }: { learning: LearningData | null; loading: boolean; generating: boolean; canGenerate: boolean; error: string; onGenerate: () => void; onToast: (message: string) => void }) {
  const packageData = learning?.learning_package;
  const concepts = packageData?.concepts || [];
  const scenarios = packageData?.scenarios || [];
  const mcqs = packageData?.mcqs || [];
  const [activeConceptIndex, setActiveConceptIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const conceptRefs = useRef<Array<HTMLElement | null>>([]);
  const selectConcept = (index: number) => {
    setActiveConceptIndex(index);
    conceptRefs.current[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };
  const selectAnswer = (mcq: Record<string, unknown>, index: number, option: unknown) => {
    if (answers[index] !== undefined) return;
    const selected = displayValue(option);
    setAnswers((current) => ({ ...current, [index]: selected }));
  };
  const answerResult = (mcq: Record<string, unknown>, index: number) => {
    const selected = answers[index];
    if (selected === undefined) return null;
    const correct = displayValue(mcq.correct_answer);
    const options = Array.isArray(mcq.options) ? mcq.options.map(displayValue) : [];
    const correctIndex = options.findIndex((option) => option === correct);
    const selectedIndex = options.findIndex((option) => option === selected);
    const isCorrect = correct === selected || (correctIndex >= 0 && correctIndex === selectedIndex) || (correct === String.fromCharCode(65 + selectedIndex));
    return { isCorrect, correct };
  };
  if (loading) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Loading your saved learning…</section>;
  if (generating) return <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Creating your personalized learning…</section>;
  if (!learning && canGenerate) return <section className="glass rounded-[22px] p-6"><p className="text-[12px] text-[#9bb0d0]">Your policy is ready. Generate a personalized learning path from its saved intelligence.</p><button onClick={onGenerate} className="btn btn-primary mt-4 rounded-full px-4 py-2.5 text-[11px] font-bold">Start Learning <ArrowRight size={13} className="ml-1 inline" /></button></section>;
  return <div><div className="learn-header"><div><span className="label-caps">Your path to confidence</span><h1 className="mt-2 font-display text-[32px] font-semibold tracking-[-.06em]">Learn your cover.</h1></div><button onClick={() => onToast(`${concepts.length} concepts · ${scenarios.length} scenarios · ${mcqs.length} checks`)} className="btn btn-ghost rounded-full px-4 py-2 text-[11px]"><Timer size={13} className="mr-1 inline" /> {mcqs.length} knowledge checks</button></div>{loading && <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Generating your learning path from your saved policy…</section>}{error && <section className="glass rounded-[22px] border border-[#ed778933] p-6 text-[12px] text-[#ffb4bf]">{error}</section>}{!loading && !error && !learning && <section className="glass rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">Upload a policy to generate your learning path.</section>}{!loading && !error && learning && <><div className="unit-tabs mb-5">{concepts.map((concept, index) => <button key={`concept-${index}`} className={`unit-tab ${index === 0 ? 'active' : ''}`}>{String(index + 1).padStart(2, '0')} {fieldText(concept, ['concept_name', 'title', 'name'], `Concept ${index + 1}`)}</button>)}</div><section className="grid gap-4 md:grid-cols-2">{concepts.map((concept, index) => <article className="glass rounded-[22px] p-5" key={`concept-card-${index}`}><span className="label-caps">Concept {index + 1}</span><h2 className="mt-2 font-display text-[19px] font-semibold">{fieldText(concept, ['concept_name', 'title', 'name'], `Concept ${index + 1}`)}</h2><p className="mt-3 text-[12px] leading-5 text-[#9aacc8]">{fieldText(concept, ['explanation', 'description', 'policy_reference', 'content', 'body'], 'This concept is based on your saved policy.')}</p></article>)}{scenarios.map((scenario, index) => <article className="glass rounded-[22px] p-5" key={`scenario-${index}`}><span className="label-caps">Scenario {index + 1}</span><h2 className="mt-2 font-display text-[19px] font-semibold">{fieldText(scenario, ['scenario_title', 'title', 'name', 'headline'], `Scenario ${index + 1}`)}</h2><p className="mt-3 text-[12px] leading-5 text-[#9aacc8]">{fieldText(scenario, ['scenario_description', 'situation', 'detail', 'explanation', 'recommended_action', 'content', 'body'], 'Review this situation using the coverage in your policy.')}</p></article>)}</section><section className="mt-5 grid gap-4">{mcqs.map((mcq, index) => <article className="glass rounded-[22px] p-5" key={`mcq-${index}`}><span className="label-caps">Knowledge check {index + 1}</span><h2 className="mt-2 font-display text-[18px] font-semibold">{fieldText(mcq, ['question', 'prompt'], `Question ${index + 1}`)}</h2><div className="mt-4 grid gap-2">{(Array.isArray(mcq.options) ? mcq.options : Array.isArray(mcq.choices) ? mcq.choices : []).map((option, optionIndex) => <button key={`option-${optionIndex}`} onClick={() => onToast('Answer recorded')} className="answer !mt-0"><span className="mr-2 text-[#6f87aa]">{String.fromCharCode(65 + optionIndex)}</span>{displayValue(option)}</button>)}</div></article>)}</section></>}</div>;
}

type ComparisonData = { summary?: string | null; changes?: Array<Record<string, unknown>> };

function ComparisonView({ onToast }: { onToast: (message: string) => void }) {
  return <DataComparisonView onToast={onToast} />;
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [oldPolicy, setOldPolicy] = useState<File | null>(null);
  const [renewedPolicy, setRenewedPolicy] = useState<File | null>(null);
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const choose = (setter: (file: File | null) => void) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/pdf';
    input.onchange = () => setter(input.files?.[0] || null);
    input.click();
  };
  const compare = async () => {
    if (!oldPolicy || !renewedPolicy) { setError('Select both policy PDFs before comparing.'); return; }
    setLoading(true); setError(''); setComparison(null);
    try {
      const formData = new FormData();
      formData.append('old_policy', oldPolicy);
      formData.append('renewed_policy', renewedPolicy);
      const response = await fetch(`${API_BASE}/api/policies/compare`, { method: 'POST', credentials: 'include', body: formData });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || 'Policy comparison failed.');
      setComparison(data.comparison || data);
      onToast(`${data.comparison?.changes?.length || 0} changes found`);
    } catch (comparisonError) {
      setError(comparisonError instanceof Error ? comparisonError.message : 'Policy comparison failed.');
    } finally { setLoading(false); }
  };
  return <div><MiniPageHeader eyebrow="Policy comparison" title="See what changed." body="Compare an older policy with its renewal before you accept the new terms." /><section className="glass rounded-[22px] p-5"><div className="grid gap-3 md:grid-cols-2"><button onClick={() => choose(setOldPolicy)} className="scan-card !p-5 text-left"><span className="label-caps">Old policy</span><strong className="mt-3 block text-[13px]">{oldPolicy?.name || 'Choose a PDF'}</strong><small className="mt-2 block text-[#7890b3]">Original policy document</small></button><button onClick={() => choose(setRenewedPolicy)} className="scan-card !p-5 text-left"><span className="label-caps">Renewed policy</span><strong className="mt-3 block text-[13px]">{renewedPolicy?.name || 'Choose a PDF'}</strong><small className="mt-2 block text-[#7890b3]">New or renewal document</small></button></div>{error && <p className="mt-4 text-[11px] text-[#ffb4bf]">{error}</p>}<button onClick={compare} disabled={loading} className="btn btn-primary mt-5 rounded-full px-5 py-2.5 text-[11px] font-bold disabled:opacity-50">{loading ? 'Comparing…' : 'Compare policies'} <ArrowRight size={13} className="ml-1 inline" /></button></section>{comparison && <section className="glass mt-5 rounded-[22px] p-5"><span className="label-caps">Comparison result</span><h2 className="mt-2 font-display text-[20px] font-semibold">{comparison.summary || 'No summary was returned.'}</h2>{comparison.changes?.length ? <div className="comparison-changes mt-5">{comparison.changes.map((change, index) => { const hiddenFields = new Set(['field', 'old_value', 'new_value', 'change_type', 'importance', 'explanation']); const extraFields = Object.entries(change).filter(([key, value]) => !hiddenFields.has(key) && value !== null && value !== undefined && value !== ''); const explanation = displayValue(change.explanation); return <article className="comparison-change" key={`change-${index}`}><div><strong>{displayValue(change.field) || `Change ${index + 1}`}</strong><small>{displayValue(change.change_type) || 'Updated'}{change.importance ? ` · ${displayValue(change.importance)}` : ''}</small></div><div className="comparison-values"><div><span>Previous</span><p>{displayValue(change.old_value) || 'Not specified'}</p></div><div><span>Renewed</span><p>{displayValue(change.new_value) || 'Not specified'}</p></div></div>{explanation && <p className="text-[11px] leading-5 text-[#9aacc8]">{explanation}</p>}{extraFields.length > 0 && <div className="mt-3 grid gap-2 border-t border-[#91b7ff1a] pt-3">{extraFields.map(([key, value]) => <div key={key} className="text-[10px] text-[#9aacc8]"><span className="mr-2 uppercase tracking-[.12em] text-[#7186a8]">{key.replaceAll('_', ' ')}</span>{displayValue(value)}</div>)}</div>}</article>; })}</div> : <p className="mt-4 text-[12px] text-[#9aacc8]">No changes were detected.</p>}</section>}</div>;
}

function DataComparisonView({ onToast }: { onToast: (message: string) => void }) {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [documents, setDocuments] = useState<Array<Record<string, any>>>([]);
  const [comparisons, setComparisons] = useState<Array<Record<string, any>>>([]);
  const [oldId, setOldId] = useState('');
  const [renewedId, setRenewedId] = useState('');
  const [loading, setLoading] = useState(false);
  const load = async () => { const [documentResponse, comparisonResponse] = await Promise.all([fetch(`${api}/api/documents`, { credentials: 'include' }), fetch(`${api}/api/policy-comparisons`, { credentials: 'include' })]); const documentData = await documentResponse.json(); const comparisonData = await comparisonResponse.json(); setDocuments(documentData.documents || []); setComparisons(comparisonData.comparisons || []); };
  useEffect(() => { void load(); }, [api]);
  const compare = async () => {
    if (!oldId || !renewedId || oldId === renewedId) return;
    setLoading(true);
    try {
      const [oldResponse, renewedResponse] = await Promise.all([fetch(`${api}/api/documents/${encodeURIComponent(oldId)}/download`, { credentials: 'include' }), fetch(`${api}/api/documents/${encodeURIComponent(renewedId)}/download`, { credentials: 'include' })]);
      if (!oldResponse.ok || !renewedResponse.ok) throw new Error('These documents are not stored as retrievable PDFs. Re-upload them before comparing.');
      const form = new FormData();
      form.append('old_policy', new File([await oldResponse.blob()], 'old-policy.pdf', { type: 'application/pdf' }));
      form.append('renewed_policy', new File([await renewedResponse.blob()], 'renewed-policy.pdf', { type: 'application/pdf' }));
      form.append('old_document_id', oldId);
      form.append('renewed_document_id', renewedId);
      const response = await fetch(`${api}/api/policies/compare`, { method: 'POST', credentials: 'include', body: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Comparison failed.');
      await load();
      onToast('Comparison saved');
    } catch (error) { onToast(error instanceof Error ? error.message : 'Comparison failed.'); } finally { setLoading(false); }
  };
  const comparableDocuments = documents.filter((document) => document.storage_available);
  return <div><MiniPageHeader eyebrow="Policy comparison" title="See what changed." body="Compare two stored policy documents and keep the result in your account." /><section className="glass rounded-[20px] p-5"><div className="grid gap-3 md:grid-cols-2"><select value={oldId} onChange={(event) => setOldId(event.target.value)} className="field-input"><option value="">Select existing PDF</option>{comparableDocuments.map((document) => <option key={document.id} value={document.id}>{document.file_name}</option>)}</select><select value={renewedId} onChange={(event) => setRenewedId(event.target.value)} className="field-input"><option value="">Select renewed PDF</option>{comparableDocuments.map((document) => <option key={document.id} value={document.id}>{document.file_name}</option>)}</select></div>{!comparableDocuments.length && <p className="mt-3 text-[11px] text-[#ffb4bf]">No retrievable stored PDFs are available. Re-upload the policies in Documents before comparing.</p>}<button disabled={loading || !oldId || !renewedId || oldId === renewedId} onClick={() => void compare()} className="btn btn-primary mt-5 rounded-full px-5 py-2.5 text-[11px] font-bold disabled:opacity-50">{loading ? 'Comparing...' : 'Compare stored policies'}</button></section><section className="glass list-panel mt-5 rounded-[20px]"><div className="panel-heading"><span className="label-caps">Saved comparisons</span></div>{comparisons.map((comparison) => <div className="list-row" key={comparison.id}><span className="row-icon cyan"><FileCheck2 size={16} /></span><div className="row-main"><strong>{comparison.old_file_name || 'Existing policy'} vs {comparison.renewed_file_name || 'Renewed policy'}</strong><small>{comparison.created_at ? new Date(comparison.created_at).toLocaleString() : 'Saved comparison'}</small></div><button className="btn btn-ghost rounded-lg px-3 py-2 text-[10px]" onClick={() => window.open(`${api}/api/policy-comparisons/${encodeURIComponent(comparison.id)}/pdf`, '_blank')}>View / Download PDF</button></div>)}{!comparisons.length && <div className="empty-inline">No comparisons saved yet.</div>}</section></div>;
}

const simSituations: Array<{ title: string; icon: IconType; headline: string; detail: string }> = [];

function SimulateView({ onToast, initialScenario }: { onToast: (message: string) => void; initialScenario?: string }) {
  return <SimulationView onToast={onToast} initialScenario={initialScenario} />;
  const [selected, setSelected] = useState(0);
  const current = simSituations[selected];
  return <div><div className="section-title"><div><span className="label-caps">Practice before it matters</span><h1 className="mt-2">What if this happens?</h1><p>Use your policy to rehearse the next right move.</p></div><span className="hidden rounded-full border border-[#f3c87333] bg-[#f3c8730c] px-3 py-2 text-[10px] text-[#efcb7a] sm:inline">EDUCATIONAL SIMULATION</span></div><section className="glass simulator rounded-[24px]"><div className="situation-grid">{simSituations.map(({ title, icon: Icon }, i) => <button key={title} onClick={() => setSelected(i)} className={`situation ${selected === i ? 'selected' : ''}`}><Icon size={18} />{title}</button>)}</div><div className="sim-result"><div className="callout"><span className="label-caps">Scenario / {String(selected + 1).padStart(2, '0')}</span><h2 className="mt-3 font-display text-[23px] font-semibold tracking-[-.05em]">{current.headline}</h2><p className="mt-2 text-[12px] leading-6 text-[#93a5c3]">{current.detail}</p><button onClick={() => onToast('+15 XP · Simulation reviewed')} className="btn btn-primary mt-5 rounded-full px-4 py-2 text-[11px] font-bold">Walk me through it <ArrowRight size={13} className="ml-1 inline" /></button></div><div className="glass-soft rounded-[17px] p-4"><span className="label-caps">Your policy says</span><div className="mt-4 space-y-3"><div className="flex items-center gap-3"><span className="grid h-7 w-7 place-items-center rounded-full bg-[#5bdfff1a] text-[#6adfff]"><ShieldCheck size={14} /></span><div><b className="block text-[11px]">Coverage check</b><span className="text-[10px] text-[#7f93b4]">Included in your plan</span></div></div><div className="flex items-center gap-3"><span className="grid h-7 w-7 place-items-center rounded-full bg-[#f0c66d14] text-[#f0c66d]"><Calculator size={14} /></span><div><b className="block text-[11px]">Room rent limit</b><span className="text-[10px] text-[#7f93b4]">₹5,000 / day</span></div></div><div className="flex items-center gap-3"><span className="grid h-7 w-7 place-items-center rounded-full bg-[#8c79ff16] text-[#a99cff]"><FileCheck2 size={14} /></span><div><b className="block text-[11px]">Next document</b><span className="text-[10px] text-[#7f93b4]">Pre-authorisation form</span></div></div></div></div></div><div className="sim-path mt-9">{['Situation', 'Coverage', 'Limits', 'Deductible', 'Documents', 'Claim'].map((step, i) => <div key={step} className="sim-step"><span>{i + 1}</span><small>{step}</small></div>)}</div><p className="mt-8 text-center text-[10px] text-[#697d9f]">Educational simulation. Actual claim decisions depend on policy terms and insurer assessment.</p></section></div>;
}

function PassportView({ onToast, onQR, passport, userName }: { onToast: (message: string) => void; onQR: () => void; passport: Record<string, unknown> | null; userName: string }) {
  const payload = passport || {};
  const productName = typeof payload.product_name === 'string' ? payload.product_name : 'Health insurance';
  const insurer = typeof payload.insurer === 'string' ? payload.insurer : 'Insurer not captured';
  const policyNumber = typeof payload.policy_number === 'string' ? payload.policy_number : 'Not available';
  const coverage = typeof payload.coverage === 'string' ? payload.coverage : 'Not specified';
  const premium = typeof payload.premium === 'string' ? payload.premium : 'Check policy schedule';
  const readiness = typeof payload.readiness === 'number' ? payload.readiness : 0;

  return <div><div className="section-title"><div><span className="label-caps">Your portable proof of preparedness</span><h1 className="mt-2">Insurance passport.</h1><p>Everything useful, without the fine-print fog.</p></div><button onClick={onQR} className="btn btn-primary rounded-full px-4 py-2.5 text-[11px] font-bold"><QrCode size={14} className="mr-1 inline" /> Temporary QR</button></div><div className="passport-wrap"><div><section className="glass passport-card rounded-[24px]"><div className="passport-top"><div className="passport-brand"><span className="logo-mark scale-[.72]"><ShieldCheck size={18} strokeWidth={1.7} /></span> INSURA</div><span className="passport-chip">PASSPORT / 01</span></div><div className="passport-name"><span className="label-caps">Policyholder</span><b>{userName}</b><span className="mt-1 block text-[11px] text-[#a4bbda]">{productName} · Individual</span></div><div className="passport-grid"><div><span>Policy number</span><b>{policyNumber}</b></div><div><span>Coverage</span><b>{coverage}</b></div><div><span>Premium</span><b>{premium}</b></div><div><span>Insurer</span><b>{insurer}</b></div><div><span>Valid until</span><b>{typeof payload.valid_until === 'string' ? payload.valid_until : 'Policy term details pending'}</b></div><div><span>Status</span><b className="text-[#84e7bf]">{typeof payload.status === 'string' ? payload.status : 'ACTIVE'}</b></div></div><div className="qr-dots" /></section><div className="mt-3 flex items-center justify-between px-1 text-[10px] text-[#7386a8]"><span><Lock size={12} className="mr-1 inline text-[#6bdfff]" /> Controlled sharing only</span><button onClick={() => onToast('Passport details copied')} className="text-[#8de9ff] hover:underline">Copy policy details</button></div></div><section className="glass readiness-card rounded-[22px]"><div className="section-title"><div><span className="label-caps">Preparedness signals</span><h2 className="mt-2">You are getting there.</h2></div><Target size={19} className="text-[#71e3bc]" /></div><div className="mt-5 flex items-center gap-4"><div className="score-ring !m-0 !h-[104px] !w-[104px]"><div><b className="!text-[25px]">{readiness}</b><span>ready</span></div></div><p className="max-w-[190px] text-[11px] leading-5 text-[#8da1c0]">Your score represents learning and preparedness progress — not an official insurance assessment.</p></div><div className="mt-6 space-y-1"><div className="score-check"><span>Policy understood</span><CheckCircle2 size={14} /></div><div className="score-check"><span>Coverage understood</span><CheckCircle2 size={14} /></div><div className="score-check"><span>Documents ready</span><CheckCircle2 size={14} /></div><div className="score-check"><span>Important clauses</span><span className="text-[#efc46f]">review</span></div></div><div className="mt-6 border-t border-[#8aaef012] pt-5"><div className="flex items-center justify-between"><span className="label-caps">Badge collection</span><span className="text-[10px] text-[#8296b7]">3 / 8 unlocked</span></div><div className="badge-list">{['Policy Starter', 'Coverage Explorer', 'Cost Smart', 'Claim Ready'].map((badge, i) => <div key={badge} title={badge} className={`badge ${i < 3 ? 'unlocked' : ''}`}>{i < 3 ? <Trophy size={17} /> : <Lock size={15} />}</div>)}</div></div></section></div></div>;
}

function MiniPageHeader({ eyebrow, title, body, action }: { eyebrow: string; title: string; body: string; action?: ReactNode }) {
  return <div className="section-title mb-5"><div><span className="label-caps">{eyebrow}</span><h1 className="mt-2">{title}</h1><p>{body}</p></div>{action}</div>;
}

function RemindersView({ onToast }: { onToast: (message: string) => void }) {
  return <DataRemindersView />;
  const [done, setDone] = useState<string[]>([]);
  const reminders = [{ id: 'premium', title: 'Premium due', detail: '₹12,000 · Care Supreme', date: '30 Sep 2026', meta: 'Due in 7 days', tone: 'gold', icon: CalendarClock }, { id: 'renewal', title: 'Policy renewal', detail: 'Care Supreme · annual renewal', date: '14 Aug 2027', meta: 'In 11 months', tone: 'blue', icon: ShieldCheck }, { id: 'claim', title: 'Claim document deadline', detail: 'Submit discharge summary', date: '20 Jan 2027', meta: 'In 4 months', tone: 'red', icon: FileCheck2 }];
  return <div><MiniPageHeader eyebrow="Reminders" title="Never miss an important insurance date." body="A quiet layer of protection for the dates that matter." action={<button onClick={() => onToast('New reminder form opened')} className="btn btn-primary rounded-full px-4 py-2.5 text-[11px] font-bold">+ Set reminder</button>} /><div className="compact-summary"><div><b>3</b><span>Upcoming</span></div><div><b>1</b><span>This week</span></div><div><b>2</b><span>Later</span></div></div><div className="secondary-grid"><section className="glass list-panel rounded-[20px]"><div className="panel-heading"><span className="label-caps">Upcoming</span><span className="status-dot blue">Synced</span></div>{reminders.filter((item) => !done.includes(item.id)).map(({ id, title, detail, date, meta, tone, icon: Icon }) => <div className="list-row reminder-row" key={id}><span className={`row-icon ${tone}`}><Icon size={16} /></span><div className="row-main"><strong>{title}</strong><small>{detail}</small><span className="row-meta">{date} · {meta}</span></div><div className="row-actions"><span className={`priority ${tone}`}>{tone === 'red' ? 'Important' : tone === 'gold' ? 'Attention' : 'Upcoming'}</span><button onClick={() => { setDone((items) => [...items, id]); onToast('Reminder completed'); }} className="icon-action" title="Mark complete"><Check size={14} /></button></div></div>)}{done.length === reminders.length && <div className="empty-inline"><CheckCircle2 size={18} /> All reminders are handled for now.</div>}</section><section className="glass settings-panel rounded-[20px]"><div className="panel-heading"><span className="label-caps">Preferences</span><Settings2 size={16} className="text-[#75ddff]" /></div>{['Premium reminders', 'Renewal reminders', 'Policy alerts', 'Daily story'].map((label, i) => <div className="setting-row" key={label}><span><strong>{label}</strong><small>{['Payment due dates', 'Renewal windows', 'Clause changes', 'One story a day'][i]}</small></span><button onClick={() => onToast(`${label} updated`)} className="switch on"><span /></button></div>)}</section></div></div>;
}

function ClaimsView({ onToast }: { onToast: (message: string) => void }) {
  return <DataClaimsView />;
  const stages = ['Incident', 'Coverage check', 'Documents', 'Verification', 'Settlement'];
  return <div><MiniPageHeader eyebrow="Claim journey" title="Know what happens next." body="A clear path for the moments when clarity matters most." action={<button onClick={() => onToast('Claim starter opened')} className="btn btn-primary rounded-full px-4 py-2.5 text-[11px] font-bold">Start a claim <ArrowRight size={13} className="ml-1 inline" /></button>} /><section className="glass claim-empty rounded-[22px]"><div className="claim-orbit"><div className="claim-shield"><ShieldCheck size={30} /></div><div className="claim-document"><FileText size={18} /></div></div><div><span className="label-caps">No active claim</span><h2 className="mt-2 font-display text-[21px] font-semibold">You’re not carrying a claim right now.</h2><p className="mt-2 max-w-[390px] text-[12px] leading-5 text-[#879bbd]">If you need to start one, INSURA will guide you through coverage, documents, and the next right action.</p></div></section><section className="glass timeline-panel rounded-[22px]"><div className="panel-heading"><div><span className="label-caps">How a claim moves</span><h2 className="mt-2 font-display text-[18px] font-semibold">From incident to settlement</h2></div><span className="status-dot teal">Educational</span></div><div className="claim-timeline">{stages.map((stage, i) => <button key={stage} onClick={() => onToast(`${stage}: what to expect`)} className={`claim-stage ${i === 0 ? 'current' : ''}`}><span>{i + 1}</span><strong>{stage}</strong><small>{i === 0 ? 'Start here' : i === 1 ? 'Check the cover' : i === 2 ? 'Gather proof' : i === 3 ? 'Insurer review' : 'Decision & payout'}</small></button>)}</div></section></div>;
}

function DocumentsView({ onUpload, onToast }: { onUpload: () => void; onToast: (message: string) => void }) {
  return <DataDocumentsView onUpload={onUpload} />;
  const docs = [{ name: 'Policy document', date: '18 Sep 2026', status: 'Verified', icon: FileText }, { name: 'Medical reports', date: '04 Sep 2026', status: '2 files', icon: Stethoscope }, { name: 'Bills & receipts', date: '29 Aug 2026', status: 'Ready', icon: ClipboardList }, { name: 'Discharge summary', date: '—', status: 'Missing', icon: FileCheck2 }, { name: 'Prescriptions', date: '12 Aug 2026', status: '1 file', icon: ClipboardCheck }];
  return <div><MiniPageHeader eyebrow="Document center" title="Keep every proof in one place." body="Policy files, medical records, and the things a claim may ask for." action={<button onClick={onUpload} className="btn btn-primary rounded-full px-4 py-2.5 text-[11px] font-bold"><UploadCloud size={13} className="mr-1 inline" /> Upload document</button>} /><section className="glass list-panel rounded-[20px]"><div className="document-toolbar"><span className="label-caps">5 documents</span><div className="flex gap-2"><button onClick={() => onToast('Document search opened')} className="btn btn-ghost rounded-lg px-3 py-2 text-[10px]">Search</button><button onClick={() => onToast('Document filter opened')} className="btn btn-ghost rounded-lg px-3 py-2 text-[10px]">Filter</button></div></div>{docs.map(({ name, date, status, icon: Icon }) => <div className="list-row" key={name}><span className="row-icon cyan"><Icon size={16} /></span><div className="row-main"><strong>{name}</strong><small>Insurance Passport · {date}</small></div><span className={`doc-status ${status === 'Missing' ? 'missing' : ''}`}>{status}</span><button onClick={() => onToast(`${name} preview opened`)} className="icon-action"><ArrowUpRight size={14} /></button></div>)}</section><div className="upload-strip glass-soft"><ScanLine size={16} className="text-[#73e0ff]" /><span><strong>AI extraction is on</strong><small>New uploads are scanned for policy dates, limits, and missing documents.</small></span><button onClick={onUpload} className="text-[11px] text-[#7de7ff]">How it works <ChevronRight size={13} className="inline" /></button></div></div>;
}

function DataDocumentsView({ onUpload }: { onUpload: () => void }) {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [documents, setDocuments] = useState<Array<Record<string, any>>>([]);
  useEffect(() => { void fetch(`${api}/api/documents`, { credentials: 'include' }).then((response) => response.json()).then((data) => setDocuments(data.documents || [])); }, [api]);
  return <div><MiniPageHeader eyebrow="Document center" title="Keep every proof in one place." body="Your stored policy documents, available after refresh and login." action={<button onClick={onUpload} className="btn btn-primary rounded-full px-4 py-2.5 text-[11px] font-bold"><UploadCloud size={13} className="mr-1 inline" /> Upload document</button>} /><section className="glass list-panel rounded-[20px]"><div className="document-toolbar"><span className="label-caps">{documents.length} stored documents</span></div>{documents.length === 0 ? <div className="empty-inline">No stored policy documents yet.</div> : documents.map((document) => <div className="list-row" key={document.id}><span className="row-icon cyan"><FileText size={16} /></span><div className="row-main"><strong>{document.file_name}</strong><small>{document.status} · {document.created_at ? new Date(document.created_at).toLocaleDateString() : 'Upload date unavailable'}</small></div><span className="doc-status">{document.storage_available ? 'Stored' : 'Processed'}</span>{document.storage_available && <button className="icon-action" title="Download document" onClick={() => window.open(`${api}/api/documents/${encodeURIComponent(document.id)}/download`, '_blank')}><ArrowUpRight size={14} /></button>}</div>)}</section></div>;
}

function DataRemindersView() {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [reminders, setReminders] = useState<Array<Record<string, any>>>([]);
  const [title, setTitle] = useState('');
  const [dueAt, setDueAt] = useState('');
  const load = () => void fetch(`${api}/api/reminders`, { credentials: 'include' }).then((response) => response.json()).then((data) => setReminders(data.reminders || []));
  useEffect(load, [api]);
  const create = async () => { if (!title.trim() || !dueAt) return; await fetch(`${api}/api/reminders`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title, due_at: new Date(dueAt).toISOString(), reminder_type: 'policy' }) }); setTitle(''); setDueAt(''); load(); };
  const complete = async (id: string) => { await fetch(`${api}/api/reminders/${encodeURIComponent(id)}`, { method: 'PATCH', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: 'completed' }) }); load(); };
  return <div><MiniPageHeader eyebrow="Reminders" title="Dates that matter, kept current." body="Reminders are stored against your account." /><section className="glass settings-panel rounded-[20px] p-5"><div className="flex flex-wrap gap-2"><input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Reminder title" className="field-input flex-1" /><input type="datetime-local" value={dueAt} onChange={(event) => setDueAt(event.target.value)} className="field-input" /><button onClick={() => void create()} className="btn btn-primary rounded-xl px-4 py-2 text-[11px]">Add reminder</button></div></section><section className="glass list-panel mt-4 rounded-[20px]">{reminders.map((reminder) => <div className="list-row" key={reminder.id}><span className="row-icon gold"><CalendarClock size={16} /></span><div className="row-main"><strong>{reminder.title}</strong><small>{reminder.reminder_type} · {new Date(reminder.due_at).toLocaleString()}</small></div><span className="doc-status">{reminder.status}</span>{reminder.status !== 'completed' && <button className="icon-action" title="Complete reminder" onClick={() => void complete(reminder.id)}><Check size={14} /></button>}</div>)}{!reminders.length && <div className="empty-inline">No reminders saved yet.</div>}</section></div>;
}

function DataHelpView() {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [tickets, setTickets] = useState<Array<Record<string, any>>>([]);
  const [message, setMessage] = useState('');
  const load = () => void fetch(`${api}/api/support/tickets`, { credentials: 'include' }).then((response) => response.json()).then((data) => setTickets(data.tickets || []));
  useEffect(load, [api]);
  const submit = async () => { if (!message.trim()) return; await fetch(`${api}/api/support/tickets`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ subject: 'INSURA support request', message }) }); setMessage(''); load(); };
  return <div><MiniPageHeader eyebrow="Help & support" title="Get a real answer." body="Ask a question and keep the support history with your account." /><section className="glass settings-panel rounded-[20px] p-5"><textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Describe what you need help with" className="field-input min-h-24 w-full" /><button onClick={() => void submit()} className="btn btn-primary mt-3 rounded-xl px-4 py-2 text-[11px]">Send support request</button></section><section className="glass list-panel mt-4 rounded-[20px]">{tickets.map((ticket) => <div className="list-row" key={ticket.id}><span className="row-icon cyan"><MessageCircle size={16} /></span><div className="row-main"><strong>{ticket.subject}</strong><small>{ticket.message}</small></div><span className="doc-status">{ticket.status}</span></div>)}{!tickets.length && <div className="empty-inline">No support requests yet.</div>}</section></div>;
}

function DataClaimsView() {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [claims, setClaims] = useState<Array<Record<string, any>>>([]);
  const [details, setDetails] = useState('');
  const load = () => void fetch(`${api}/api/claims`, { credentials: 'include' }).then((response) => response.json()).then((data) => setClaims(data.claims || []));
  useEffect(load, [api]);
  const start = async () => { if (!details.trim()) return; await fetch(`${api}/api/claims`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ details }) }); setDetails(''); load(); };
  return <div><MiniPageHeader eyebrow="Claim journey" title="Record and follow a claim." body="Claim records use your saved policy and remain linked to your account." /><section className="glass settings-panel rounded-[20px] p-5"><textarea value={details} onChange={(event) => setDetails(event.target.value)} placeholder="Describe the incident or claim" className="field-input min-h-24 w-full" /><button onClick={() => void start()} className="btn btn-primary mt-3 rounded-xl px-4 py-2 text-[11px]">Start claim record</button></section><section className="glass list-panel mt-4 rounded-[20px]">{claims.map((claim) => <div className="list-row" key={claim.id}><span className="row-icon red"><ShieldAlert size={16} /></span><div className="row-main"><strong>{claim.status}</strong><small>{claim.details}</small></div><span className="doc-status">Saved</span></div>)}{!claims.length && <div className="empty-inline">No claim records yet.</div>}</section></div>;
}

function DataSettingsView() {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [settings, setSettings] = useState<Record<string, boolean>>({});
  useEffect(() => { void fetch(`${api}/api/settings`, { credentials: 'include' }).then((response) => response.json()).then((data) => setSettings(data.settings || {})); }, [api]);
  const update = async (key: string) => { const next = { ...settings, [key]: !settings[key] }; setSettings(next); await fetch(`${api}/api/settings`, { method: 'PATCH', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(next) }); };
  return <div><MiniPageHeader eyebrow="Settings" title="Make INSURA work your way." body="Preferences are saved to your account." /><section className="glass settings-panel rounded-[20px]">{['premium_reminder', 'renewal_reminder', 'claim_updates', 'policy_sharing'].map((key) => <div className="setting-row" key={key}><span><strong>{key.replaceAll('_', ' ')}</strong><small>Persisted account preference</small></span><button onClick={() => void update(key)} className={`switch ${settings[key] ? 'on' : ''}`}><span /></button></div>)}</section></div>;
}

function AssistantView({ onToast }: { onToast: (message: string) => void }) {
  return <PolicyAssistantView onToast={onToast} />;
  const [question, setQuestion] = useState<string | null>(null);
  const prompts = ['What does my deductible mean?', 'What is excluded?', 'What documents do I need?', 'How does my claim work?'];
  return <div><MiniPageHeader eyebrow="Policy assistant" title="Ask about your insurance policy." body="A focused intelligence layer — your structured journey stays in charge." action={<span className="status-dot teal">Policy connected</span>} /><div className="assistant-layout"><section className="glass chat-panel rounded-[22px]"><div className="chat-head"><span className="assistant-avatar"><BrainCircuit size={16} /></span><div><strong>INSURA assistant</strong><small>Answers grounded in Care Supreme</small></div><span className="status-dot teal">Online</span></div><div className="chat-body"><div className="chat-bubble assistant">Hi Riya. Ask me anything about your policy — I’ll point you back to the source.</div>{question && <><div className="chat-bubble user">{question}</div><div className="chat-bubble assistant">Your policy mentions this under <strong>Coverage & cost sharing</strong>. I can explain the practical next step without replacing your insurer’s decision.</div><div className="source-ref"><FileText size={13} /><span>Policy Document · Page 4</span><ChevronRight size={13} /></div></>}</div><div className="prompt-grid">{prompts.map((prompt) => <button key={prompt} onClick={() => { setQuestion(prompt); onToast('Policy reference found'); }}>{prompt}<ArrowUpRight size={12} /></button>)}</div></section><section className="glass reference-panel rounded-[22px]"><span className="label-caps">Policy references</span><h2 className="mt-2 font-display text-[18px] font-semibold">Useful, not overwhelming.</h2><div className="reference-row"><span className="row-icon cyan"><ShieldAlert size={15} /></span><span><strong>Waiting period</strong><small>Found in policy clauses · Page 7</small></span></div><div className="reference-row"><span className="row-icon gold"><Calculator size={15} /></span><span><strong>₹10,000 deductible</strong><small>Costs & limits · Page 4</small></span></div><div className="reference-row"><span className="row-icon violet"><FileCheck2 size={15} /></span><span><strong>Claim documents</strong><small>Claim process · Page 12</small></span></div></section></div></div>;
}

function RewardsView({ onToast, progress }: { onToast: (message: string) => void; progress: ProgressionData | null }) {
  const badges = [
    { name: 'Policy Starter', group: 'Learning', xp: '+40 XP', unlocked: true },
    { name: 'Coverage Explorer', group: 'Policy knowledge', xp: '+60 XP', unlocked: true },
    { name: 'Cost Smart', group: 'Preparedness', xp: '+80 XP', unlocked: true },
    { name: 'Exclusion Expert', group: 'Policy knowledge', xp: '+100 XP', unlocked: false },
    { name: 'Claim Ready', group: 'Claims', xp: '+120 XP', unlocked: false },
    { name: 'Document Ready', group: 'Preparedness', xp: '+100 XP', unlocked: false },
    { name: 'Policy Detective', group: 'Learning', xp: '+160 XP', unlocked: false },
    { name: 'Insurance Pro', group: 'Policy knowledge', xp: '+240 XP', unlocked: false },
  ];
  const totalXp = Number(progress?.xp ?? 0);
  const streak = Number(progress?.streak ?? 0);
  const nextMilestone = Number(progress?.next_milestone_xp ?? 0);
  const earnedBadges = Number(progress?.badges?.length ?? 0) || 3;
  return <div><MiniPageHeader eyebrow="Rewards" title="Progress worth keeping." body="Three systems. One calmer insurance experience." action={<div className="reward-total"><Trophy size={15} /> {totalXp.toLocaleString()} XP</div>} /><div className="reward-stats"><div className="glass-soft"><span className="label-caps">Knowledge streak</span><b><Flame size={20} className="text-[#ffb24e]" /> {streak} days</b><small>Best: 21 days</small></div><div className="glass-soft"><span className="label-caps">Next milestone</span><b><Target size={18} className="text-[#71e3bc]" /> +{nextMilestone} XP</b><small>Keep learning to unlock the next badge</small></div><div className="glass-soft"><span className="label-caps">Badges earned</span><b><BadgeCheck size={18} className="text-[#72dfff]" /> {earnedBadges} / {badges.length}</b><small>Keep learning to unlock more</small></div></div><div className="badge-board glass rounded-[22px]"><div className="panel-heading"><div><span className="label-caps">Achievement collection</span><h2 className="mt-2 font-display text-[18px] font-semibold">Small wins, made visible.</h2></div><span className="text-[10px] text-[#8194b4]">Tap a badge for details</span></div><div className="badge-collection">{badges.map((badge) => <button key={badge.name} onClick={() => onToast(badge.unlocked ? `${badge.name} · ${badge.xp}` : `${badge.name} unlocks with more learning`)} className={`achievement ${badge.unlocked ? 'earned' : 'locked'}`}><span className="achievement-mark">{badge.unlocked ? <Trophy size={19} /> : <Lock size={16} />}</span><span><strong>{badge.name}</strong><small>{badge.group}</small><em>{badge.xp}</em></span></button>)}</div></div></div>;
}

function ProfileView({ onToast, userName, userEmail, progress }: { onToast: (message: string) => void; userName: string; userEmail?: string; progress: ProgressionData | null }) {
  const profileItems = [
    { label: 'Insurance Passport', detail: 'Policy details and QR sharing', icon: ShieldCheck },
    { label: 'Personal information', detail: 'Name, email and phone', icon: UserRound },
    { label: 'Insurance information', detail: 'Care Supreme coverage', icon: FileText },
    { label: 'Notification preferences', detail: 'Your reminder choices', icon: Bell },
    { label: 'Security & privacy', detail: 'Password and privacy', icon: Lock },
  ];
  const initials = userName.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase() || 'U';
  const readiness = Math.max(0, Math.min(100, Number(progress?.readiness ?? 0)));
  const xp = Number(progress?.xp ?? 0);
  const streak = Number(progress?.streak ?? 0);
  const badgeCount = Math.max(0, Number(progress?.badges?.length ?? 0));
  return <div><MiniPageHeader eyebrow="Profile" title={userName} body="Your insurance identity, progress, and personal details." action={<button onClick={() => onToast('Profile editor opened')} className="btn btn-ghost rounded-full px-4 py-2.5 text-[11px]">Edit profile</button>} /><div className="profile-layout"><section className="glass profile-card rounded-[22px]"><div className="profile-head"><span className="profile-avatar">{initials}</span><div><h2>{userName}</h2><span>Policyholder · Member since {new Date().toLocaleString('en-IN', { month: 'short', year: 'numeric' })}</span></div></div><div className="profile-facts"><div><span>Email</span><b>{userEmail || 'your email'}</b></div><div><span>XP</span><b>{xp.toLocaleString()} XP</b></div><div><span>Streak</span><b>🔥 {streak} days</b></div><div><span>Readiness</span><b className="text-[#74e4bb]">{readiness} / 100</b></div></div></section><section className="glass profile-menu rounded-[22px]">{profileItems.map(({ label, detail, icon: Icon }) => <button key={label} onClick={() => onToast(`${label} opened`)}><span className="row-icon cyan"><Icon size={15} /></span><span><strong>{label}</strong><small>{detail}</small></span><ChevronRight size={14} /></button>)}</section></div></div>;
}

function SettingsView({ onToast }: { onToast: (message: string) => void }) {
  return <DataSettingsView />;
  const settings = ['Daily insurance story', 'Policy tips', 'Premium reminder', 'Renewal reminder', 'Claim updates'];
  return <div><MiniPageHeader eyebrow="Settings" title="Make INSURA work your way." body="Notifications, learning preferences, privacy, and account controls." /><div className="settings-layout"><section className="glass settings-nav rounded-[20px]">{['Notifications', 'Learning', 'Insurance', 'Privacy & security', 'Appearance', 'Language', 'Account'].map((item, i) => <button className={i === 0 ? 'active' : ''} key={item}>{item}<ChevronRight size={13} /></button>)}</section><section className="glass settings-panel rounded-[20px]"><div className="panel-heading"><div><span className="label-caps">Notifications</span><h2 className="mt-2 font-display text-[18px] font-semibold">Choose what reaches you.</h2></div><Bell size={16} className="text-[#71ddff]" /></div>{settings.map((item, i) => <div className="setting-row" key={item}><span><strong>{item}</strong><small>{['One story to keep your streak alive', 'Important clauses and policy changes', 'Payment due dates', 'Renewal windows', 'Claim stage changes'][i]}</small></span><button onClick={() => onToast(`${item} updated`)} className={`switch ${i === 3 ? '' : 'on'}`}><span /></button></div>)}</section></div></div>;
}

function HelpView({ onToast }: { onToast: (message: string) => void }) {
  return <DataHelpView />;
  return <div><MiniPageHeader eyebrow="Help & support" title="A clear answer is part of protection." body="Browse the basics or talk to the INSURA team." /><div className="help-grid">{[{ title: 'Frequently asked questions', body: 'Quick answers about the product and your policy.', icon: CircleHelp }, { title: 'Insurance basics', body: 'A calm place to learn the language of cover.', icon: BookOpen }, { title: 'Contact support', body: 'Reach the team when you need a human answer.', icon: MessageCircle }, { title: 'Report a problem', body: 'Tell us what felt confusing or didn’t work.', icon: ShieldAlert }].map(({ title, body, icon: Icon }) => <button key={title} onClick={() => onToast(`${title} opened`)} className="glass help-card"><span className="row-icon cyan"><Icon size={17} /></span><span><strong>{title}</strong><small>{body}</small></span><ArrowUpRight size={14} /></button>)}</div></div>;
}

function ProfilePanel({ onClose, onNavigate, onSignOut, onToast, userName, progress }: { onClose: () => void; onNavigate: (view: View) => void; onSignOut: () => void; onToast: (message: string) => void; userName: string; progress: ProgressionData }) {
  const sections: { label: string; detail: string; icon: IconType; view?: View }[] = [
    { label: 'Insurance Passport', detail: 'Policy details and temporary QR', icon: ShieldCheck, view: 'passport' },
    { label: 'Learning progress', detail: 'Your path, XP, and current lesson', icon: BookOpen, view: 'learn' },
    { label: 'Badges', detail: `${Math.max(0, Number(progress?.badges?.length ?? 0))} unlocked achievements`, icon: Trophy, view: 'rewards' },
    { label: 'Notifications', detail: 'Reminders and important dates', icon: Bell, view: 'reminders' },
    { label: 'Security', detail: 'Privacy and account protection', icon: Lock, view: 'settings' },
    { label: 'Settings', detail: 'Preferences and appearance', icon: Settings2, view: 'settings' },
  ];
  const initials = userName.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase() || 'U';
  return <div className="profile-panel-overlay" onClick={onClose}><aside className="profile-drawer glass" onClick={(event) => event.stopPropagation()}><div className="profile-drawer-top"><span className="label-caps">Your INSURA profile</span><button className="close-btn" onClick={onClose}><X size={16} /></button></div><div className="profile-drawer-user"><span className="profile-avatar">{initials}</span><div><h2>{userName}</h2><span>Policyholder · Member since {new Date().toLocaleString('en-IN', { month: 'short', year: 'numeric' })}</span></div></div><div className="drawer-metrics"><div><span>Readiness</span><b>{Math.max(0, Math.min(100, Number(progress?.readiness ?? 0)))}/100</b></div><div><span>XP</span><b>{Number(progress?.xp ?? 0).toLocaleString()}</b></div><div><span>Streak</span><b>🔥 {Number(progress?.streak ?? 0)}</b></div></div><div className="drawer-sections">{sections.map(({ label, detail, icon: Icon, view }) => <button key={label} onClick={() => { if (view) { onNavigate(view); onClose(); } else onToast(`${label} opened`); }}><span className="row-icon cyan"><Icon size={15} /></span><span><strong>{label}</strong><small>{detail}</small></span><ChevronRight size={14} /></button>)}</div><button className="drawer-signout" onClick={onSignOut}><ArrowLeft size={14} /> Sign out of INSURA</button></aside></div>;
}

function AuthModal({ mode, setMode, onClose, onSuccess }: { mode: AuthMode; setMode: (mode: AuthMode) => void; onClose: () => void; onSuccess: (user?: { name?: string; email?: string }, created?: boolean) => void }) {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const submitAuth = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const endpoint = mode === 'register' ? `${API_BASE}/register` : `${API_BASE}/login`;
      const payload = mode === 'register'
        ? { name, email, password }
        : { email, password };

      const response = await fetch(endpoint, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.success !== true) {
        setError(data.error || 'Something went wrong. Please try again.');
        return;
      }

      onSuccess({
        name: data.user?.name || name || 'User',
        email: data.user?.email || email || '',
      }, mode === 'register');
    } catch {
      setError('Could not reach the INSURA backend. Please make sure the Flask app is running.');
    } finally {
      setSubmitting(false);
    }
  };

  return <div className="overlay"><div className="glass auth-shell"><div className="auth-art"><button className="border-0 bg-transparent p-0" onClick={onClose}><Logo /></button><div className="mt-7"><span className="label-caps">The calmer side of insurance</span><h2 className="mt-3 max-w-[240px] font-display text-[28px] font-semibold leading-[1.05] tracking-[-.05em]">Your cover, in a language you can use.</h2><p className="mt-4 max-w-[260px] text-[11px] leading-5 text-[#8ea3c4]">Build your Insurance Passport once. Keep learning at your own pace.</p></div><div className="-ml-[74px] mt-1"><ProtectionScene small /></div></div><div className="auth-form relative"><button className="close-btn" onClick={onClose} aria-label="Close"><X size={16} /></button><span className="label-caps">Welcome to INSURA</span><h1 className="mt-3 font-display text-[30px] font-semibold tracking-[-.06em]">{mode === 'signin' ? 'Welcome back.' : 'Start your insurance journey.'}</h1><p className="mt-2 text-[12px] text-[#8295b4]">{mode === 'signin' ? 'Pick up where you left off.' : "Let's build your Insurance Passport."}</p><div className="auth-tabs"><button type="button" className={mode === 'signin' ? 'active' : ''} onClick={() => setMode('signin')}>Sign in</button><button type="button" className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>Create account</button></div><form onSubmit={submitAuth}><div className="space-y-3">{mode === 'register' && <div className="field"><label>Full name</label><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Riya Menon" /></div>}<div className="field"><label>Email address</label><input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="riya@example.com" /></div><div className="field"><label>Password</label><div className="relative"><input value={password} onChange={(e) => setPassword(e.target.value)} className="pr-10" type={showPassword ? 'text' : 'password'} placeholder="••••••••" /><button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 border-0 bg-transparent p-0 text-[#7690b2]">{showPassword ? <EyeOff size={15} /> : <Eye size={15} />}</button></div></div>{error && <div className="rounded-xl border border-[#ff6b6b33] bg-[#ff6b6b14] px-3 py-2 text-[11px] leading-5 text-[#ffc7ca]">{error}</div>}<button type="submit" className="btn btn-primary mt-3 w-full rounded-full py-2.5 text-[11px] font-bold" disabled={submitting}>{submitting ? 'Please wait...' : mode === 'signin' ? 'Sign in' : 'Create account'}</button><button type="button" onClick={() => { window.location.href = `${API_BASE}/auth/google`; }} className="btn btn-ghost mt-2 w-full rounded-full py-2.5 text-[11px] font-bold">Continue with Google</button></div></form></div></div></div>;
} function LessonModal({ onClose, onComplete }: { onClose: () => void; onComplete: () => void }) {
  const [selected, setSelected] = useState<string | null>(null);
  const choices = ['The amount you pay before cover begins', 'A discount on your premium', 'The total amount your insurer pays'];
  return <div className="overlay"><div className="glass modal wide"><button className="close-btn" onClick={onClose}><X size={16} /></button><div className="mb-6 flex items-center gap-3"><span className="lesson-icon"><Calculator size={20} /></span><div><span className="label-caps">Unit 04 · Costs & limits</span><h2 className="mt-1 font-display text-[22px] font-semibold">What is a deductible?</h2></div></div><div className="rounded-[17px] border border-[#8ab3ea18] bg-[#0a1328a6] p-5"><span className="label-caps">Real-life scenario</span><p className="mt-3 text-[14px] leading-6 text-[#cad8ec]">You have an <strong className="text-white">₹80,000</strong> hospital bill. Your policy has a <strong className="text-[#76e5ff]">₹10,000 deductible</strong>.</p></div><div className="mt-7"><span className="label-caps">Quick check</span><h3 className="mt-2 font-display text-[20px] font-semibold tracking-[-.03em]">How does the deductible affect you?</h3><div className="mt-4 grid gap-2">{choices.map((choice, i) => <button key={choice} onClick={() => setSelected(choice)} className={`answer !mt-0 ${selected === choice ? (i === 0 ? 'correct' : 'wrong') : ''}`}><span className="mr-2 text-[#6f87aa]">{String.fromCharCode(65 + i)}</span>{choice}{selected === choice && <span className="float-right">{i === 0 ? '✓' : '×'}</span>}</button>)}</div></div>{selected && <div className={`mt-5 rounded-[14px] border p-4 text-[11px] leading-5 ${selected === choices[0] ? 'border-[#67dfb533] bg-[#4ed59e0e] text-[#9beacd]' : 'border-[#ed778933] bg-[#ed77890c] text-[#ffb4bf]'}`}>{selected === choices[0] ? 'Exactly. You pay the first ₹10,000, then the policy responds according to its terms.' : 'The deductible is the portion you pay first — it is not a premium discount or the full bill.'}</div>}<div className="mt-7 flex items-center justify-between"><span className="text-[11px] text-[#8296b7]"><Zap size={13} className="mr-1 inline text-[#f1ca74]" /> +20 XP on completion</span><button disabled={selected !== choices[0]} onClick={onComplete} className="btn btn-primary rounded-full px-4 py-2.5 text-[11px] font-bold disabled:cursor-not-allowed disabled:opacity-40">Complete lesson <ArrowRight size={13} className="ml-1 inline" /></button></div></div></div>;
}

function QRModal({ onClose }: { onClose: () => void }) {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const qrUrl = `${API_BASE}/api/passport/qr?ts=${Date.now()}`;

  return <div className="overlay"><div className="glass modal text-center"><button className="close-btn" onClick={onClose}><X size={16} /></button><span className="label-caps">Temporary access token</span><h2 className="mt-3 font-display text-[26px] font-semibold tracking-[-.05em]">Share with confidence.</h2><p className="mx-auto mt-2 max-w-[320px] text-[12px] leading-5 text-[#879ab9]">This QR provides controlled access to selected insurance information for 10 minutes.</p><div className="mx-auto my-7 grid h-[180px] w-[180px] place-items-center rounded-[20px] border border-[#78e8ff3f] bg-[#e5fbff] p-4 shadow-[0_0_45px_#4bd7ff2c]"><img src={qrUrl} alt="Insurance Passport QR" className="h-full w-full rounded-[14px] object-cover" /></div><div className="flex items-center justify-center gap-2 text-[10px] text-[#7e91b2]"><Clock3 size={13} className="text-[#72e3ff]" /> Expires in 09:58</div><button className="btn btn-ghost mt-5 rounded-full px-5 py-2.5 text-[11px]" onClick={onClose}>Done</button></div></div>;
}

function UploadModal({ onClose, onComplete }: { onClose: () => void; onComplete: (output?: Record<string, unknown> | MouseEvent<HTMLButtonElement>, policyId?: string) => void }) {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [stage, setStage] = useState<'upload' | 'scan' | 'done'>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysisOutput, setAnalysisOutput] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please choose a PDF policy document first.');
      return;
    }

    setSubmitting(true);
    setError('');
    setStage('scan');

    try {
      const formData = new FormData();
      formData.append('policy', selectedFile);

      const response = await fetch(`${API_BASE}/api/policies/analyze`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || 'Your policy could not be uploaded.');
      }
      if (!data.output || typeof data.output !== 'object' || Array.isArray(data.output)) {
        throw new Error('Policy analysis returned an invalid result.');
      }
      const output = data.output as Record<string, unknown>;
      setAnalysisOutput(output);

      window.setTimeout(() => {
        setStage('done');
        onComplete(output, data.policy_id);
      }, 1800);
    } catch (uploadError) {
      setStage('upload');
      setError(uploadError instanceof Error ? uploadError.message : 'Your policy could not be uploaded.');
    } finally {
      setSubmitting(false);
    }
  };

  const openFilePicker = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/pdf';
    input.onchange = (event) => {
      const target = event.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file) {
        setSelectedFile(file);
        setError('');
      }
    };
    input.click();
  };

  return <div className="overlay"><div className="glass modal"><button className="close-btn" onClick={onClose}><X size={16} /></button>{stage === 'upload' && <><span className="label-caps">Add your policy</span><h2 className="mt-3 font-display text-[25px] font-semibold tracking-[-.05em]">Let's start with the fine print.</h2><p className="mt-2 text-[12px] leading-5 text-[#879ab9]">Upload your PDF policy. INSURA will turn it into your Insurance Passport.</p><div className="scan-card mt-6"><div><span className="upload-icon"><UploadCloud size={25} /></span><h3 className="font-display text-[16px] font-semibold">Drop your policy here</h3><p className="mt-2 text-[11px] text-[#7890b3]">PDF only · up to 20 MB</p><button type="button" onClick={openFilePicker} className="btn btn-primary mt-5 rounded-full px-4 py-2.5 text-[11px] font-bold">{selectedFile ? selectedFile.name : 'Choose a PDF file'}</button>{selectedFile && <div className="mt-3 rounded-lg border border-[#8dc9ff2d] bg-[#0f1e36] px-3 py-2 text-[10px] text-[#b7d4ff]">{selectedFile.name}</div>}{error && <p className="mt-3 text-[10px] text-[#ffb4bf]">{error}</p>}<button type="button" disabled={!selectedFile || submitting} onClick={handleUpload} className="btn btn-primary mt-5 rounded-full px-4 py-2.5 text-[11px] font-bold disabled:opacity-50">{submitting ? 'Uploading...' : 'Upload and continue'}</button><p className="mt-3 text-[10px] text-[#5e7498]">Your document will be stored and sent to INSURA automation.</p></div></div></>}{stage === 'scan' && <div className="py-12 text-center"><div className="upload-icon relative mx-auto"><ScanLine size={25} /><span className="absolute left-1/2 top-0 h-full w-px bg-[#9cf2ff] shadow-[0_0_15px_#9cf2ff]" /></div><span className="label-caps">Step 2 of 3</span><h2 className="mt-3 font-display text-[25px] font-semibold">Understanding your coverage…</h2><p className="mt-3 text-[12px] text-[#879ab9]">Scanning clauses and finding what matters.</p><div className="progress-track mx-auto mt-6 max-w-[280px]"><span className="animate-pulse" style={{ width: '70%' }} /></div></div>}{stage === 'done' && <div className="py-10 text-center"><span className="mx-auto grid h-16 w-16 place-items-center rounded-[22px] border border-[#73e6c155] bg-[#6de0b814] text-[#82e8c2] shadow-[0_0_30px_#62dfb329]"><Check size={29} /></span><span className="label-caps mt-5 block">Passport ready</span><h2 className="mt-3 font-display text-[25px] font-semibold">Your policy is understood.</h2><p className="mx-auto mt-2 max-w-[300px] text-[12px] leading-5 text-[#879ab9]">Your PDF was saved securely and sent to the INSURA workflow for review.</p><button type="button" onClick={onComplete} className="btn btn-primary mt-6 rounded-full px-5 py-2.5 text-[11px] font-bold">Open dashboard</button></div>}</div></div>;
}
export default function Home() {
  const [mode, setMode] = useState<'landing' | 'app'>('landing');
  const [active, setActive] = useState<View>('home');
  const [moreOpen, setMoreOpen] = useState(false);
  const [authMode, setAuthMode] = useState<AuthMode | null>(null);
  const [modal, setModal] = useState<'qr' | 'upload' | null>(null);
  const [profilePanel, setProfilePanel] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [hasUploadedPolicy, setHasUploadedPolicy] = useState(false);
  const [policy, setPolicy] = useState<PolicyOutput | null>(null);
  const [policyId, setPolicyId] = useState<string | null>(null);
  const [learningGenerationId, setLearningGenerationId] = useState<string | null>(null);
  const [learning, setLearning] = useState<LearningData | null>(null);
  const [learningLoading, setLearningLoading] = useState(false);
  const [learningGenerating, setLearningGenerating] = useState(false);
  const [learningError, setLearningError] = useState('');
  const [dashboardScenario, setDashboardScenario] = useState('');
  const [sessionUser, setSessionUser] = useState<{ name?: string; email?: string } | null>(null);
  const [passport, setPassport] = useState<Record<string, unknown> | null>(null);
  const API_BASE = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const userDisplayName = sessionUser?.name || 'Riya Menon';
  const userEmail = sessionUser?.email || 'riya@example.com';
  const [progress, setProgress] = useState<ProgressionData>({ xp: 0, streak: 0, readiness: 0, completed_levels: 0, total_levels: 5, learning_percentage: 0, level: 1, next_milestone_xp: 100, badges: [] });
  const [xp, setXp] = useState(0);
  const [streak, setStreak] = useState(0);
  const showToast = (message: string) => { setToast(message); window.setTimeout(() => setToast(null), 2600); };
  useEffect(() => {
    const handleProgressUpdate = (event: Event) => {
      const nextProgress = (event as CustomEvent<ProgressionData>).detail;
      if (!nextProgress) return;
      setProgress(nextProgress);
      setXp(Number(nextProgress.xp || 0));
      setStreak(Number(nextProgress.streak || 0));
    };
    window.addEventListener('insura:progress-updated', handleProgressUpdate);
    return () => window.removeEventListener('insura:progress-updated', handleProgressUpdate);
  }, []);
  const refreshDashboard = async (allowFreshAuthentication = false) => {
    if (!isAuthenticated && !allowFreshAuthentication) return false;
    let hasPolicy = false;
    try {
      const dashboardResponse = await fetch(`${API_BASE}/api/dashboard`, { credentials: 'include' });
      const dashboardData = await dashboardResponse.json().catch(() => ({}));
      if (dashboardResponse.ok) {
        hasPolicy = Boolean(dashboardData.policy_id || dashboardData.policy);
        setHasUploadedPolicy(hasPolicy);
        setPolicy((dashboardData.policy as PolicyOutput) || null);
        setPolicyId(dashboardData.policy_id || null);
        setLearning((dashboardData.learning as LearningData) || null);
        setLearningGenerationId(dashboardData.learning_generation_id || null);
        const nextProgress = {
          xp: Number(dashboardData.progress?.xp || dashboardData.stats?.xp || 0),
          streak: Number(dashboardData.progress?.streak || 0),
          readiness: Number(dashboardData.progress?.readiness || 0),
          completed_levels: Number(dashboardData.progress?.completed_levels || 0),
          total_levels: Number(dashboardData.progress?.total_levels || 5),
          learning_percentage: Number(dashboardData.progress?.learning_percentage || 0),
          level: Number(dashboardData.progress?.level || 1),
          next_milestone_xp: Number(dashboardData.progress?.next_milestone_xp || 100),
          badges: Array.isArray(dashboardData.progress?.badges) ? dashboardData.progress.badges : [],
          completed_learning_items: Array.isArray(dashboardData.progress?.completed_learning_items) ? dashboardData.progress.completed_learning_items : [],
        } as ProgressionData;
        setProgress(nextProgress);
        setXp(Number(nextProgress.xp || 0));
        setStreak(Number(nextProgress.streak || 0));
      }

      const passportResponse = await fetch(`${API_BASE}/api/passport`, { credentials: 'include' });
      const passportData = await passportResponse.json().catch(() => ({}));
      if (passportResponse.ok) {
        setPassport((passportData.passport as Record<string, unknown>) || null);
      }
    } catch {
      // Ignore dashboard refresh errors when the backend is unavailable.
    }
    return hasPolicy;
  };
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const shouldOpenApp = params.get('view') === 'app' || params.get('auth') === 'success';

    const checkSession = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/session`, { credentials: 'include' });
        const data = await response.json().catch(() => ({}));
        if (data.authenticated) {
          setSessionUser(data.user || null);
          setIsAuthenticated(true);
          setHasUploadedPolicy(Boolean(data.has_uploaded_policy));
          setPolicyId(data.policy_id || null);
          setLearningGenerationId(data.learning_generation_id || null);
          const nextProgress = {
            xp: Number(data.progress?.xp || 0),
            streak: Number(data.progress?.streak || 0),
            readiness: Number(data.progress?.readiness || 0),
            completed_levels: Number(data.progress?.completed_levels || 0),
            total_levels: Number(data.progress?.total_levels || 5),
            learning_percentage: Number(data.progress?.learning_percentage || 0),
            level: Number(data.progress?.level || 1),
            next_milestone_xp: Number(data.progress?.next_milestone_xp || 100),
            badges: Array.isArray(data.progress?.badges) ? data.progress.badges : [],
            completed_learning_items: Array.isArray(data.progress?.completed_learning_items) ? data.progress.completed_learning_items : [],
          } as ProgressionData;
          setProgress(nextProgress);
          setXp(Number(nextProgress.xp || 0));
          setStreak(Number(nextProgress.streak || 0));
          if (data.policy_id) {
            const policyResponse = await fetch(`${API_BASE}/api/policies/${encodeURIComponent(data.policy_id)}`, { credentials: 'include' });
            const policyData = await policyResponse.json().catch(() => ({}));
            if (policyResponse.ok && policyData.output) setPolicy(policyData.output as PolicyOutput);
          }
          if (data.learning_generation_id) {
            const learningResponse = await fetch(`${API_BASE}/api/learning/${encodeURIComponent(data.learning_generation_id)}`, { credentials: 'include' });
            const learningData = await learningResponse.json().catch(() => ({}));
            if (learningResponse.ok && learningData.learning) setLearning(learningData.learning as LearningData);
          }
          const passportResponse = await fetch(`${API_BASE}/api/passport`, { credentials: 'include' });
          const passportData = await passportResponse.json().catch(() => ({}));
          if (passportResponse.ok && passportData.passport) setPassport(passportData.passport as Record<string, unknown>);
          setMode('landing');
          setActive('home');
          return;
        }
      } catch {
        // Ignore session check failures when the backend is unavailable.
      }

      if (shouldOpenApp) {
        setIsAuthenticated(true);
        setMode('landing');
        setActive('home');
      }
    };

    checkSession();
  }, []);
  const generateLearning = async () => {
    if (!isAuthenticated || !policyId || !policy || learningGenerationId || learningGenerating) return;
    setLearningGenerating(true); setLearningError('');
      try {
        const response = await fetch(`${API_BASE}/api/learning/generate`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ policy_intelligence: policy, policy_id: policyId }) });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || 'Learning generation failed.');
        setLearningGenerationId(data.learning_generation_id || null);
        setLearning(data.learning as LearningData);
      } catch (generationError) {
        setLearningError(generationError instanceof Error ? generationError.message : 'Learning generation failed.');
      } finally { setLearningGenerating(false); }
  };
  const start = async (user?: { name?: string; email?: string }, created = false) => {
    if (user) setSessionUser(user);
    setIsAuthenticated(true);
    setMode('landing');
    setActive('home');
    setAuthMode(null);
    const hasPolicy = await refreshDashboard(true);
    if (created && !hasPolicy) setModal('upload');
  };
  const openAuth = (auth: AuthMode) => setAuthMode(auth);
  const startJourneyIfSignedIn = async () => {
    if (!isAuthenticated) {
      showToast('Please sign in first');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/session`, { credentials: 'include' });
      const data = await response.json().catch(() => ({}));
      const hasPolicy = response.ok && data.authenticated === true && Boolean(data.has_uploaded_policy);
      setHasUploadedPolicy(hasPolicy);
      if (hasPolicy && data.policy_status === 'processing') {
        showToast('Your policy is still being processed.');
        return;
      }
      if (hasPolicy) {
        setMode('app');
        setActive('home');
      } else {
        setModal('upload');
      }
    } catch {
      showToast('Could not verify your saved policy. Please try again.');
    }
  };
  const completeJourney = () => { setModal(null); setMode('app'); setActive('home'); };
  const content = active === 'home' ? <HomeView xp={xp} streak={streak} progress={progress} onToast={showToast} onLesson={() => setActive('learn')} onSimulation={(scenario) => { setDashboardScenario(scenario); setActive('simulate'); }} userName={userDisplayName} policy={policy} learning={learning} /> : active === 'learn' ? <LearnView learning={learning} completedLearningItems={progress.completed_learning_items} loading={learningLoading} generating={learningGenerating} canGenerate={Boolean(policyId && policy)} error={learningError} onGenerate={generateLearning} onToast={showToast} /> : active === 'compare' ? <ComparisonView onToast={showToast} /> : active === 'simulate' ? <SimulateView onToast={showToast} initialScenario={dashboardScenario} /> : active === 'passport' ? <PassportView onToast={showToast} onQR={() => setModal('qr')} passport={passport} userName={userDisplayName} /> : active === 'rewards' ? <RewardsView onToast={showToast} progress={progress} /> : active === 'reminders' ? <RemindersView onToast={showToast} /> : active === 'claims' ? <ClaimsView onToast={showToast} /> : active === 'documents' ? <DocumentsView onUpload={() => setModal('upload')} onToast={showToast} /> : active === 'assistant' ? <AssistantView onToast={showToast} /> : active === 'profile' ? <ProfileView onToast={showToast} userName={userDisplayName} userEmail={userEmail} progress={progress} /> : active === 'settings' ? <SettingsView onToast={showToast} /> : <HelpView onToast={showToast} />;
  if (mode === 'landing') return <><Landing onStart={startJourneyIfSignedIn} onAuth={openAuth} authenticated={isAuthenticated} userName={userDisplayName} />{authMode && <AuthModal mode={authMode} setMode={setAuthMode} onClose={() => setAuthMode(null)} onSuccess={start} />}{modal === 'upload' && <UploadModal onClose={() => { setModal(null); }} onComplete={(output, uploadedPolicyId) => { setPolicy(output as PolicyOutput); setPolicyId(uploadedPolicyId || null); setHasUploadedPolicy(true); completeJourney(); showToast('Policy uploaded and your dashboard is ready.'); }} />}</>;
  return <div className="app-shell min-h-screen"><AmbientDots /><div className="dashboard-frame"><TopBar active={active} onBrand={() => setMode('landing')} onProfile={() => setProfilePanel(true)} userName={userDisplayName} /><main>{content}</main></div><CommandDock active={active} setActive={setActive} moreOpen={moreOpen} setMoreOpen={setMoreOpen} />{profilePanel && <ProfilePanel onClose={() => setProfilePanel(false)} onNavigate={setActive} onToast={showToast} onSignOut={() => { setProfilePanel(false); setIsAuthenticated(false); setHasUploadedPolicy(false); setPolicy(null); setPolicyId(null); setLearning(null); setLearningGenerationId(null); setSessionUser(null); setMode('landing'); window.location.href = `${API_BASE}/logout`; }} userName={userDisplayName} progress={progress} />} {modal === 'qr' && <QRModal onClose={() => setModal(null)} />}{modal === 'upload' && <UploadModal onClose={() => setModal(null)} onComplete={(output, uploadedPolicyId) => { setPolicy(output as PolicyOutput); setPolicyId(uploadedPolicyId || null); setHasUploadedPolicy(true); setModal(null); setActive('passport'); showToast('Passport updated from your policy'); }} />} {toast && <div className="toast"><CheckCircle2 size={15} className="text-[#76e5bc" />{toast}</div>}</div>;
}


