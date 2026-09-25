import { useEffect, useState } from "react";
import {
  ArrowRight,
  Check,
  FileText,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

type SimulationResult = {
  scenario: string;
  coverage_status:
    | "covered"
    | "not_specified"
    | "excluded"
    | "partially_applicable"
    | "likely_covered"
    | "potentially_covered"
    | "not_found"
    | "likely_excluded";
  confidence: "high" | "medium" | "low";
  explanation: string;
  policy_basis: string[];
  financial_considerations: Record<string, string>;
  waiting_period: string;
  documents: string[];
  next_steps: string[];
  missing_information: string[];
  limits: string[];
  claim_path: string[];
};

type Props = { onToast: (message: string) => void; initialScenario?: string };

const scenarios = [
  {
    category: "Hospitalization",
    label: "3-day hospital stay",
    prompt: "What if I am hospitalized for 3 days?",
  },
  {
    category: "Hospitalization",
    label: "Hospital bill",
    prompt: "What if my hospital bill is high?",
  },
  {
    category: "Hospitalization",
    label: "ICU treatment",
    prompt: "What if I need ICU treatment?",
  },
  {
    category: "Hospitalization",
    label: "Non-network hospital",
    prompt: "What if I choose a non-network hospital?",
  },
  {
    category: "Accident",
    label: "Accident admission",
    prompt: "What if I have an accident and need hospitalization?",
  },
  {
    category: "Accident",
    label: "Accident surgery",
    prompt: "What if an accident requires surgery?",
  },
  {
    category: "Emergency",
    label: "Emergency treatment",
    prompt: "What if I need emergency treatment?",
  },
  {
    category: "Emergency",
    label: "Sudden admission",
    prompt: "What if I am admitted suddenly?",
  },
  {
    category: "Treatment",
    label: "New treatment",
    prompt: "What if I need a treatment I have never used before?",
  },
  {
    category: "Treatment",
    label: "Waiting period",
    prompt: "What if the treatment has a waiting period?",
  },
  {
    category: "Surgery",
    label: "Planned surgery",
    prompt: "What if I need surgery?",
  },
  {
    category: "Surgery",
    label: "Surgery cost",
    prompt: "What if the surgery costs more than expected?",
  },
  {
    category: "Claims",
    label: "Required documents",
    prompt: "What documents will I need?",
  },
  {
    category: "Claims",
    label: "Cashless treatment",
    prompt: "What if I use cashless treatment?",
  },
  {
    category: "Claims",
    label: "Already paid",
    prompt: "What if I have already paid the hospital?",
  },
];

const statusCopy: Record<SimulationResult["coverage_status"], string> = {
  covered: "Covered according to the extracted policy",
  not_specified: "Not specified in your uploaded policy",
  excluded: "Excluded according to the extracted policy",
  partially_applicable: "Partially applicable",
  likely_covered: "Likely covered, subject to policy conditions",
  potentially_covered: "Potentially covered",
  not_found: "Not specified in your uploaded policy",
  likely_excluded: "Potentially excluded according to the extracted policy",
};

async function postProgress(
  activityType: string,
  activityId: string,
  body: Record<string, unknown> = {}
) {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const response = await fetch(`${api}/api/progression`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      activity_type: activityType,
      activity_id: activityId,
      ...body,
    }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok)
    throw new Error(data.error || "Progress could not be saved.");
  if (data.progress)
    window.dispatchEvent(
      new CustomEvent("insura:progress-updated", { detail: data.progress })
    );
  return data;
}

export default function SimulationView({ onToast, initialScenario = "" }: Props) {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [category, setCategory] = useState("Hospitalization");
  const [scenario, setScenario] = useState(scenarios[0].prompt);
  const [customScenario, setCustomScenario] = useState("");
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [scenarioId, setScenarioId] = useState("");
  const [simulationId, setSimulationId] = useState("");
  const [activeStep, setActiveStep] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (initialScenario) setCustomScenario(initialScenario);
  }, [initialScenario]);

  const analyze = async () => {
    const selectedScenario = customScenario.trim() || scenario;
    if (!selectedScenario) return;
    setLoading(true);
    setError("");
    setResult(null);
    setActiveStep(0);
    setCompleted(false);
    try {
      const response = await fetch(`${api}/api/simulations/analyze`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: selectedScenario }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok)
        throw new Error(
          data.error || "INSURA could not analyze this situation."
        );
      setResult(data.result as SimulationResult);
      setScenarioId(String(data.scenario_id || ""));
      setSimulationId(String(data.simulation_id || ""));
      onToast("Policy-grounded simulation ready");
    } catch (simulationError) {
      setError(
        simulationError instanceof Error
          ? simulationError.message
          : "INSURA could not analyze this situation."
      );
    } finally {
      setLoading(false);
    }
  };

  const activateStep = async (step: number) => {
    if (!result) return;
    setActiveStep(step);
    if (step !== 5 || completed || !scenarioId) return;
    try {
      const completion = await postProgress(
        "simulation_completion",
        scenarioId,
        {
          completed_steps: 6,
          simulation: { simulation_id: simulationId, result },
        }
      );
      const bonus = await postProgress(
        "simulation_steps_bonus",
        `${scenarioId}:steps`
      );
      setCompleted(true);
      onToast(
        completion.awarded || bonus.awarded
          ? "Simulation complete · XP saved"
          : "Simulation already completed"
      );
    } catch (progressError) {
      onToast(
        progressError instanceof Error
          ? progressError.message
          : "Simulation progress could not be saved."
      );
    }
  };

  const filteredScenarios = scenarios.filter(
    item => item.category === category
  );
  const steps = [
    ["Situation", result?.scenario || scenario],
    [
      "Coverage",
      result ? statusCopy[result.coverage_status] : "Waiting for your scenario",
    ],
    [
      "Limits",
      result?.limits.length
        ? result.limits.join(" · ")
        : "Not specified in your uploaded policy.",
    ],
    [
      "Your cost",
      result
        ? Object.values(result.financial_considerations).join(" · ")
        : "Not specified in your uploaded policy.",
    ],
    [
      "Documents",
      result?.documents.length
        ? result.documents.join(" · ")
        : "Not specified in your uploaded policy.",
    ],
    [
      "Claim",
      result?.claim_path.length
        ? result.claim_path.join(" · ")
        : "Not specified in your uploaded policy.",
    ],
  ];

  return (
    <div>
      <div className="section-title">
        <div>
          <span className="label-caps">Interactive policy rehearsal</span>
          <h1 className="mt-2">What if this happens?</h1>
          <p>Rehearse a real situation using your policy.</p>
        </div>
        <span className="status-dot teal">POLICY GROUNDED</span>
      </div>
      {!result && (
        <section className="glass simulator rounded-[24px] p-5">
          <div className="situation-grid">
            {[
              "Hospitalization",
              "Accident",
              "Emergency",
              "Treatment",
              "Surgery",
              "Claims",
            ].map(item => (
              <button
                key={item}
                onClick={() => setCategory(item)}
                className={`situation ${category === item ? "selected" : ""}`}
              >
                <ShieldCheck size={16} />
                {item}
              </button>
            ))}
          </div>
          <div className="mt-6">
            <span className="label-caps">Quick scenarios</span>
            <div className="mt-3 grid gap-3 md:grid-cols-3">
              {filteredScenarios.map(item => (
                <button
                  key={item.prompt}
                  onClick={() => {
                    setScenario(item.prompt);
                    setCustomScenario(item.prompt);
                  }}
                  className={`scan-card p-4 text-left ${scenario === item.prompt && customScenario === item.prompt ? "border-[#72ddff88]" : ""}`}
                >
                  <FileText size={16} className="text-[#70ddff]" />
                  <strong className="mt-3 block text-[12px]">
                    {item.label}
                  </strong>
                  <small className="mt-1 block text-[#8398ba]">
                    {item.prompt}
                  </small>
                </button>
              ))}
            </div>
          </div>
          <div className="mt-6">
            <span className="label-caps">Or ask your own question</span>
            <textarea
              value={customScenario}
              onChange={event => setCustomScenario(event.target.value)}
              className="mt-3 min-h-[90px] w-full rounded-[16px] border border-[#8ab3ea22] bg-[#0a1328a6] p-4 text-[12px] text-white outline-none"
              placeholder="Example: I need to be hospitalized for 4 days after an accident. How would my policy help?"
            />
            <button
              onClick={analyze}
              disabled={loading}
              className="btn btn-primary mt-4 rounded-full px-5 py-2.5 text-[11px] font-bold disabled:opacity-50"
            >
              {loading ? "Analyzing your policy..." : "Analyze with my policy"}{" "}
              <ArrowRight size={13} className="ml-1 inline" />
            </button>
          </div>
          {error && <p className="mt-4 text-[11px] text-[#ffb4bf]">{error}</p>}
        </section>
      )}
      {loading && (
        <section className="glass mt-5 rounded-[22px] p-6 text-[12px] text-[#9bb0d0]">
          <Sparkles size={17} className="mb-3 text-[#72ddff]" />
          INSURA is checking your policy, coverage, limits, exclusions, and
          claim details...
        </section>
      )}
      {result && (
        <div className="grid gap-5 lg:grid-cols-[.8fr_1.2fr]">
          <section className="glass rounded-[22px] p-5">
            <span className="label-caps">Simulation flow</span>
            <div className="mt-5 space-y-2">
              {steps.map(([label, detail], index) => (
                <button
                  key={label}
                  onClick={() => activateStep(index)}
                  className={`flex w-full items-start gap-3 rounded-[14px] border p-3 text-left transition ${index <= activeStep ? "border-[#70ddff66] bg-[#5bdfff0d]" : "border-[#8ab3ea16]"}`}
                >
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full border border-[#70ddff55] text-[10px] text-[#78e4ff]">
                    {index < activeStep || completed ? (
                      <Check size={12} />
                    ) : (
                      index + 1
                    )}
                  </span>
                  <span>
                    <strong className="block text-[11px]">{label}</strong>
                    <small className="mt-1 block text-[#8ba0c1]">
                      {detail}
                    </small>
                  </span>
                </button>
              ))}
            </div>
            <button
              onClick={() => {
                setResult(null);
                setCompleted(false);
              }}
              className="btn btn-ghost mt-5 rounded-full px-4 py-2 text-[11px]"
            >
              Try another scenario
            </button>
          </section>
          <section className="glass rounded-[22px] p-5">
            <span className="label-caps">What your policy says</span>
            <div className="mt-3 flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-full border border-[#70ddff55] text-[#70ddff]">
                <ShieldAlert size={19} />
              </span>
              <div>
                <h2 className="font-display text-[21px] font-semibold">
                  {statusCopy[result.coverage_status]}
                </h2>
                <small className="text-[#8ca1c2]">
                  Confidence: {result.confidence}
                </small>
              </div>
            </div>
            <p className="mt-5 text-[13px] leading-6 text-[#c0cee3]">
              {result.explanation}
            </p>
            <div className="mt-5 rounded-[16px] border border-[#70ddff22] bg-[#5bdfff08] p-4">
              <span className="label-caps">Based on your policy</span>
              {result.policy_basis.length ? (
                <ul className="mt-3 space-y-2 text-[11px] text-[#b8d7eb]">
                  {result.policy_basis.map(item => (
                    <li key={item}>✓ {item}</li>
                  ))}
                </ul>
              ) : (
                <p className="mt-3 text-[11px] text-[#a7b7d0]">
                  INSURA couldn't find supporting policy facts for this
                  situation.
                </p>
              )}
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {Object.entries(result.financial_considerations).map(
                ([label, value]) => (
                  <div
                    key={label}
                    className="rounded-[13px] border border-[#8ab3ea18] p-3"
                  >
                    <span className="label-caps">
                      {label.replaceAll("_", " ")}
                    </span>
                    <strong className="mt-2 block text-[11px] text-[#d4e5f5]">
                      {value}
                    </strong>
                  </div>
                )
              )}
            </div>
            <div className="mt-5 rounded-[14px] border border-[#f3c87333] bg-[#f3c87308] p-4 text-[11px] leading-5 text-[#d6c58f]">
              Educational simulation. Actual claim decisions depend on your
              policy terms, insurer assessment, and claim circumstances.
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
