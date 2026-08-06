import type { Chat, StudyMode } from "../api";

interface ChatHeaderProps {
    chat: Chat;

    isUpdating: boolean;

    onStudyModeChange: (mode: StudyMode) => void;
}

const studyModes: StudyMode[] = [
    "Learn",
    "Exam",
    "Revision",
    "Clinical",
    "Viva",
];

export default function ChatHeader({
    chat,
    isUpdating,
    onStudyModeChange,
}: ChatHeaderProps) {
    return (
        <header className="border-b border-slate-200 bg-white px-6 py-5 dark:border-slate-800 dark:bg-slate-950">

            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

                <div>

                    <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                        {chat.title}
                    </h1>

                    <p className="mt-1 text-sm text-slate-500">
                        Medical AI Tutor
                    </p>

                </div>

                <div className="flex flex-wrap items-center gap-4">

                    {/* Study Mode */}

                    <div className="flex flex-col">

                        <label className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                            Study Mode
                        </label>

                        <select
                            value={chat.study_mode}
                            disabled={isUpdating}
                            onChange={(event) =>
                                onStudyModeChange(
                                    event.target.value as StudyMode,
                                )
                            }
                            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm dark:border-slate-700 dark:bg-slate-900"
                        >
                            {studyModes.map((mode) => (
                                <option
                                    key={mode}
                                    value={mode}
                                >
                                    {mode}
                                </option>
                            ))}
                        </select>

                    </div>

                    {/* Subject */}

                    <div className="flex flex-col">

                        <label className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                            Subject
                        </label>

                        <div className="rounded-xl border border-slate-300 bg-slate-100 px-4 py-2 text-sm text-slate-500 dark:border-slate-700 dark:bg-slate-900">
                            {chat.subject ?? "General"}
                        </div>

                    </div>

                </div>

            </div>

        </header>
    );
}