import type { Chat } from '../api'

interface ChatSidebarProps {
    chats: Chat[]
    selectedChat: Chat | null

    isLoading: boolean
    isCreating: boolean
    isDisabled: boolean

    onNewChat: () => void
    onSelectChat: (chat: Chat) => void
}

export default function ChatSidebar({
    chats,
    selectedChat,
    isLoading,
    isCreating,
    isDisabled,
    onNewChat,
    onSelectChat,
}: ChatSidebarProps) {
    return (
        <aside className="flex w-80 shrink-0 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">

            {/* Header */}
            <div className="border-b border-slate-200 p-4 dark:border-slate-800">

                <button
                    type="button"
                    onClick={onNewChat}
                    disabled={isCreating || isDisabled}
                    className="w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
                >
                    {isCreating ? "Creating..." : "+ New Chat"}
                </button>

                {/* Search (Coming Soon) */}
                <input
                    disabled
                    placeholder="Search chats (Coming Soon)"
                    className="mt-4 w-full rounded-xl border border-slate-300 bg-slate-100 px-4 py-2 text-sm text-slate-500 outline-none dark:border-slate-700 dark:bg-slate-900"
                />
            </div>

            {/* Chat List */}
            <div className="flex-1 overflow-y-auto p-3">

                <p className="mb-3 px-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Recent Chats
                </p>

                {isLoading ? (
                    <p className="px-2 text-sm text-slate-500">
                        Loading chats...
                    </p>
                ) : chats.length === 0 ? (
                    <p className="px-2 text-sm text-slate-500">
                        No chats yet.
                    </p>
                ) : (
                    <div className="space-y-2">

                        {chats.map((chat) => {

                            const active =
                                selectedChat?.id === chat.id

                            return (
                                <button
                                    key={chat.id}
                                    type="button"
                                    disabled={isDisabled}
                                    onClick={() => onSelectChat(chat)}
                                    className={[
                                        "w-full rounded-xl border px-4 py-3 text-left transition",

                                        active
                                            ? "border-blue-500 bg-blue-50 dark:border-blue-500 dark:bg-blue-950/40"
                                            : "border-transparent hover:border-slate-300 hover:bg-slate-100 dark:hover:border-slate-700 dark:hover:bg-slate-900",
                                    ].join(" ")}
                                >
                                    <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">
                                        {chat.title}
                                    </p>

                                    <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">

                                        <span>
                                            {chat.study_mode}
                                        </span>

                                        {chat.subject && (
                                            <>
                                                <span>•</span>

                                                <span className="truncate">
                                                    {chat.subject}
                                                </span>
                                            </>
                                        )}

                                        {chat.is_pinned && (
                                            <>
                                                <span>📌</span>
                                            </>
                                        )}

                                    </div>

                                </button>
                            )
                        })}

                    </div>
                )}

            </div>

        </aside>
    )
}