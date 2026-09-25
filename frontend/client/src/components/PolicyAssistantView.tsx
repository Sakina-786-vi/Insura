import { Fragment, useEffect, useRef, useState, type ReactNode } from "react";
import { BrainCircuit, Languages, MessageSquarePlus, Mic, Pencil, Send, Square, Volume2 } from "lucide-react";

type Props = { onToast: (message: string) => void };
type Chat = { id: string; title: string; updated_at?: string };
type Message = { id: string; role: "user" | "assistant"; content: string; created_at?: string };
const languages = [{ code: "en-IN", label: "English" }, { code: "hi-IN", label: "Hindi" }, { code: "mr-IN", label: "Marathi" }];

const prompts = ["What does my deductible mean?", "What is a copay?", "What is generally excluded?", "How does a claim work?"];

function renderInline(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => part.startsWith("**") && part.endsWith("**")
    ? <strong key={index}>{part.slice(2, -2)}</strong>
    : <Fragment key={index}>{part}</Fragment>);
}

function AssistantContent({ content }: { content: string }) {
  const lines = content.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const blocks: ReactNode[] = [];
  let listItems: string[] = [];

  const flushList = () => {
    if (!listItems.length) return;
    blocks.push(<ul key={`list-${blocks.length}`}>{listItems.map((item, index) => <li key={index}>{renderInline(item)}</li>)}</ul>);
    listItems = [];
  };

  lines.forEach((line, index) => {
    const bullet = line.match(/^[-*]\s+(.+)/);
    if (bullet) {
      listItems.push(bullet[1]);
      return;
    }
    flushList();
    const heading = line.match(/^\*\*(\d+\.\s+.+?)\*\*$/) || line.match(/^(#{1,3})\s+(.+)/);
    if (heading) {
      const title = heading.length === 3 ? heading[2] : heading[1].replace(/^#+\s+/, "");
      blocks.push(<h3 key={`heading-${index}`}>{renderInline(title)}</h3>);
      return;
    }
    blocks.push(<p key={`paragraph-${index}`}>{renderInline(line)}</p>);
  });
  flushList();
  return <div className="assistant-rich-text">{blocks}</div>;
}

export default function PolicyAssistantView({ onToast }: Props) {
  const api = import.meta.env.VITE_API_BASE_URL || window.location.origin;
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [titleDraft, setTitleDraft] = useState("");
  const [language, setLanguage] = useState("en-IN");
  const [recording, setRecording] = useState(false);
  const [translatedMessages, setTranslatedMessages] = useState<Record<string, string>>({});
  const recorderRef = useRef<MediaRecorder | null>(null);

  const loadChat = async (chat: Chat) => {
    setError("");
    const response = await fetch(`${api}/api/chats/${encodeURIComponent(chat.id)}`, { credentials: "include" });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "This chat could not be opened.");
    setActiveChat(data.chat);
    setMessages(Array.isArray(data.chat?.messages) ? data.chat.messages : []);
    window.sessionStorage.setItem("insura-active-chat", chat.id);
  };

  useEffect(() => {
    let cancelled = false;
    const loadHistory = async () => {
      try {
        const response = await fetch(`${api}/api/chats`, { credentials: "include" });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(data.error || "Chat history could not be loaded.");
        if (cancelled) return;
        const savedChats = Array.isArray(data.chats) ? data.chats : [];
        setChats(savedChats);
        const selectedId = window.sessionStorage.getItem("insura-active-chat");
        const selected = savedChats.find((chat: Chat) => chat.id === selectedId) || savedChats[0];
        if (selected) await loadChat(selected);
      } catch (historyError) {
        if (!cancelled) setError(historyError instanceof Error ? historyError.message : "Chat history could not be loaded.");
      } finally {
        if (!cancelled) setLoadingHistory(false);
      }
    };
    void loadHistory();
    return () => { cancelled = true; };
  }, [api]);

  const newChat = () => {
    setActiveChat(null);
    setMessages([]);
    setQuestion("");
    setError("");
    window.sessionStorage.removeItem("insura-active-chat");
  };

  const stopRecording = () => {
    recorderRef.current?.stop();
    recorderRef.current = null;
    setRecording(false);
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices?.getUserMedia || recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];
      recorder.ondataavailable = (event) => { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const formData = new FormData();
        formData.append("audio", new Blob(chunks, { type: recorder.mimeType || "audio/webm" }), "voice.webm");
        formData.append("language_code", language);
        try {
          const response = await fetch(`${api}/api/sarvam/transcribe`, { method: "POST", credentials: "include", body: formData });
          const data = await response.json().catch(() => ({}));
          if (!response.ok) throw new Error(data.error || "Voice transcription is unavailable.");
          setQuestion(String(data.transcript || ""));
        } catch (transcriptionError) {
          setError(transcriptionError instanceof Error ? transcriptionError.message : "Voice transcription is unavailable.");
        }
      };
      recorderRef.current = recorder;
      recorder.start();
      setError("");
      setRecording(true);
    } catch {
      setError("Microphone access was not available.");
    }
  };

  const translateMessage = async (message: Message) => {
    if (message.role !== "assistant" || language === "en-IN") return;
    try {
      const response = await fetch(`${api}/api/sarvam/translate`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: message.content, source_language_code: "en-IN", target_language_code: language }) });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || "Translation is unavailable.");
      setTranslatedMessages((current) => ({ ...current, [message.id]: String(data.translated_text || "") }));
    } catch (translationError) {
      setError(translationError instanceof Error ? translationError.message : "Translation is unavailable.");
    }
  };

  const speakMessage = async (message: Message) => {
    try {
      const response = await fetch(`${api}/api/sarvam/speak`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: translatedMessages[message.id] || message.content, target_language_code: language }) });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || "Speech playback is unavailable.");
      }
      const audio = new Audio(URL.createObjectURL(await response.blob()));
      audio.onended = () => URL.revokeObjectURL(audio.src);
      await audio.play();
    } catch (speechError) {
      setError(speechError instanceof Error ? speechError.message : "Speech playback is unavailable.");
    }
  };

  const send = async () => {
    const prompt = question.trim();
    if (!prompt || loading) return;
    setQuestion("");
    setLoading(true);
    setError("");
    try {
      let chat = activeChat;
      if (!chat) {
        const createResponse = await fetch(`${api}/api/chats`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
        const createData = await createResponse.json().catch(() => ({}));
        if (!createResponse.ok) throw new Error(createData.error || "A new chat could not be created.");
        const createdChat = createData.chat as Chat;
        chat = createdChat;
        setActiveChat(chat);
        setChats((current) => [createdChat, ...current]);
        window.sessionStorage.setItem("insura-active-chat", createdChat.id);
      }
      if (!chat) throw new Error("A chat could not be selected.");
      const chatId = chat.id;
      setMessages((current) => [...current, { id: `pending-${Date.now()}`, role: "user", content: prompt }]);
      const response = await fetch(`${api}/api/chats/${encodeURIComponent(chatId)}/messages`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content: prompt }) });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || "INSURA could not answer that right now.");
      setMessages((current) => [...current.filter((message) => !message.id.startsWith("pending-")), data.user_message, data.assistant_message]);
      setActiveChat(data.chat);
      setChats((current) => current.map((item) => item.id === chat?.id ? data.chat : item).sort((a, b) => String(b.updated_at || "").localeCompare(String(a.updated_at || ""))));
      onToast("Response saved to your chat");
    } catch (sendError) {
      setMessages((current) => current.map((message) => message.id.startsWith("pending-") ? { ...message, id: `saved-${Date.now()}` } : message));
      setError(sendError instanceof Error ? sendError.message : "INSURA could not answer that right now.");
    } finally {
      setLoading(false);
    }
  };

  const rename = async (chat: Chat) => {
    const title = titleDraft.trim();
    setEditingId(null);
    if (!title || title === chat.title) return;
    const response = await fetch(`${api}/api/chats/${encodeURIComponent(chat.id)}`, { method: "PATCH", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title }) });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) { setError(data.error || "Chat title could not be saved."); return; }
    setChats((current) => current.map((item) => item.id === chat.id ? data.chat : item));
    setActiveChat(data.chat);
  };

  return <div>
    <div className="section-title"><div><span className="label-caps">Insurance assistant</span><h1 className="mt-2">A conversation you can return to.</h1><p>Policy questions stay grounded in your account. General insurance questions are welcome too.</p></div><span className="status-dot teal">GROQ AI CONNECTED</span></div>
    <div className="assistant-shell">
      <section className="glass chat-panel rounded-[22px]"><div className="chat-head"><span className="assistant-avatar"><BrainCircuit size={16} /></span><div><strong>INSURA assistant</strong><small>Private policy context stays on the backend</small></div><span className="status-dot teal">Online</span></div><div className="chat-body">{messages.length === 0 && <div className="chat-bubble assistant">Ask about your policy or a general insurance concept. I will keep policy-specific answers limited to what is stored.</div>}{messages.map((message) => <div className={`chat-bubble ${message.role}`} key={message.id}>{message.role === "assistant" ? <><AssistantContent content={translatedMessages[message.id] || message.content} /><div className="mt-2 flex gap-2"><button type="button" className="btn btn-ghost rounded-lg px-2 py-1" aria-label="Translate response" title="Translate response" onClick={() => void translateMessage(message)}><Languages size={13} /></button><button type="button" className="btn btn-ghost rounded-lg px-2 py-1" aria-label="Play response" title="Play response" onClick={() => void speakMessage(message)}><Volume2 size={13} /></button></div></> : message.content}</div>)}{loading && <div className="chat-bubble assistant typing"><span /> <span /> <span /> Checking your question...</div>}{error && <div className="chat-bubble assistant text-[#ffb4bf]">{error}</div>}</div><div className="prompt-grid">{prompts.map((prompt) => <button key={prompt} onClick={() => setQuestion(prompt)}>{prompt}</button>)}</div><form className="assistant-composer" onSubmit={(event) => { event.preventDefault(); void send(); }}><select aria-label="Voice language" value={language} onChange={(event) => setLanguage(event.target.value)} className="rounded-xl border border-[#8ab3ea22] bg-[#0a1328a6] px-2 py-2 text-[11px] text-white outline-none">{languages.map((item) => <option key={item.code} value={item.code}>{item.label}</option>)}</select><input value={question} onChange={(event) => setQuestion(event.target.value)} disabled={loading || recording} className="min-w-0 flex-1 rounded-xl border border-[#8ab3ea22] bg-[#0a1328a6] px-3 py-2 text-[11px] text-white outline-none" placeholder="Type your insurance question..." /><button type="button" disabled={loading} className="btn btn-ghost rounded-xl px-3 py-2 disabled:opacity-50" aria-label={recording ? "Stop recording" : "Start voice input"} title={recording ? "Stop recording" : "Start voice input"} onClick={() => recording ? stopRecording() : void startRecording()}>{recording ? <Square size={14} /> : <Mic size={14} />}</button><button type="submit" disabled={!question.trim() || loading || recording} className="btn btn-primary rounded-xl px-3 py-2 disabled:opacity-50" aria-label="Send question"><Send size={14} /></button></form></section>
      <aside className="glass assistant-history rounded-[22px]"><div className="assistant-history-head"><span className="label-caps">Chat history</span><button className="btn btn-primary assistant-new-chat" onClick={newChat}><MessageSquarePlus size={14} /> New chat</button></div><div className="assistant-chat-list">{loadingHistory ? <span className="assistant-empty">Loading chats...</span> : chats.length === 0 ? <span className="assistant-empty">Your saved chats will appear here.</span> : chats.map((chat) => <div className={`assistant-chat-row ${activeChat?.id === chat.id ? "active" : ""}`} key={chat.id}><button onClick={() => void loadChat(chat)} className="assistant-chat-open"><strong>{chat.title}</strong><small>{chat.updated_at ? new Date(chat.updated_at).toLocaleDateString() : ""}</small></button><button className="assistant-edit" title="Rename chat" onClick={() => { setEditingId(chat.id); setTitleDraft(chat.title); }}><Pencil size={12} /></button>{editingId === chat.id && <form className="assistant-title-editor" onSubmit={(event) => { event.preventDefault(); void rename(chat); }}><input autoFocus value={titleDraft} onChange={(event) => setTitleDraft(event.target.value)} /><button aria-label="Save title"><Send size={11} /></button></form>}</div>)}</div></aside>
    </div>
  </div>;
}
