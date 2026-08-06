import {
    type FormEvent,
    useEffect,
    useRef,
    useState,
} from 'react'

import {
    createChat,
    getChat,
    getChats,
    sendMessage,
    type Chat,
    type ChatMessage,
} from './api'


export default function AITutorPage() {
    const [chats, setChats] = useState<Chat[]>([])
    const [selectedChat, setSelectedChat] = useState<Chat | null>(null)
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [messageInput, setMessageInput] = useState('')

    const [isLoadingChats, setIsLoadingChats] = useState(true)
    const [isLoadingMessages, setIsLoadingMessages] = useState(false)
    const [isCreating, setIsCreating] = useState(false)
    const [isSending, setIsSending] = useState(false)

    const [error, setError] = useState<string | null>(null)

    const messagesEndRef = useRef<HTMLDivElement | null>(null)

    useEffect(() => {
        void loadChats()
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: 'smooth',
        })
    }, [messages, isSending])


    async function loadChats() {
        try {
            setIsLoadingChats(true)
            setError(null)

            const data = await getChats()

            setChats(data)
        } catch {
            setError('Unable to load your chats.')
        } finally {
            setIsLoadingChats(false)
        }
    }


    async function handleSelectChat(chat: Chat) {
        if (isSending) {
            return
        }

        try {
            setSelectedChat(chat)
            setMessages([])
            setIsLoadingMessages(true)
            setError(null)

            const history = await getChat(
                chat.id,
                20,
                0,
            )

            setSelectedChat(history.session)
            setMessages(history.messages)
        } catch {
            setError('Unable to load this conversation.')
        } finally {
            setIsLoadingMessages(false)
        }
    }


    async function handleNewChat() {
        if (isSending) {
            return
        }

        try {
            setIsCreating(true)
            setError(null)

            const chat = await createChat({
                title: 'New Chat',
                study_mode: 'Learn',
            })

            setChats((currentChats) => [
                chat,
                ...currentChats,
            ])

            setSelectedChat(chat)
            setMessages([])
            setMessageInput('')
        } catch {
            setError('Unable to create a new chat.')
        } finally {
            setIsCreating(false)
        }
    }


    async function handleSendMessage(
        event: FormEvent<HTMLFormElement>,
    ) {
        event.preventDefault()

        const content = messageInput.trim()

        if (
            !selectedChat ||
            !content ||
            isSending
        ) {
            return
        }

        const chatId = selectedChat.id

        /*
         * Temporary message so the user's question appears
         * immediately while the backend generates the AI response.
         */
        const temporaryUserMessage: ChatMessage = {
            id: -Date.now(),
            role: 'user',
            content,
            created_at: new Date().toISOString(),
        }

        setMessages((currentMessages) => [
            ...currentMessages,
            temporaryUserMessage,
        ])

        setMessageInput('')
        setError(null)
        setIsSending(true)

        try {
            await sendMessage(
                chatId,
                content,
            )

            /*
             * Reload the conversation after the request completes.
             * The backend saves both:
             * 1. user message
             * 2. assistant response
             *
             * Reloading also replaces our temporary message with
             * the real database message.
             */
            const history = await getChat(
                chatId,
                20,
                0,
            )

            setSelectedChat(history.session)
            setMessages(history.messages)

            /*
             * The backend may automatically change "New Chat"
             * to a title based on the first question.
             * Update the sidebar with the latest session.
             */
            setChats((currentChats) =>
                currentChats.map((chat) =>
                    chat.id === history.session.id
                        ? history.session
                        : chat,
                ),
            )
        } catch {
            /*
             * Remove the temporary message if sending failed,
             * and restore the text so the user can retry.
             */
            setMessages((currentMessages) =>
                currentMessages.filter(
                    (message) =>
                        message.id !== temporaryUserMessage.id,
                ),
            )

            setMessageInput(content)

            setError(
                'Unable to send your message. Please try again.',
            )
        } finally {
            setIsSending(false)
        }
    }


    return (
        <div className="flex min-h-[calc(100vh-4rem)] overflow-hidden rounded-xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">

            {/* Chat sidebar */}
            <aside className="flex w-72 shrink-0 flex-col border-r border-slate-200 dark:border-slate-800">

                <div className="p-4">
                    <button
                        type="button"
                        onClick={handleNewChat}
                        disabled={isCreating || isSending}
                        className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {isCreating
                            ? 'Creating...'
                            : '+ New Chat'}
                    </button>
                </div>


                <div className="flex-1 overflow-y-auto px-3 pb-4">
                    <p className="mb-3 px-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Recent Chats
                    </p>

                    {isLoadingChats ? (
                        <p className="px-2 text-sm text-slate-500">
                            Loading chats...
                        </p>
                    ) : chats.length === 0 ? (
                        <p className="px-2 text-sm text-slate-500">
                            No chats yet.
                        </p>
                    ) : (
                        <div className="space-y-1">
                            {chats.map((chat) => {
                                const isSelected =
                                    selectedChat?.id === chat.id

                                return (
                                    <button
                                        key={chat.id}
                                        type="button"
                                        disabled={isSending}
                                        onClick={() => {
                                            void handleSelectChat(chat)
                                        }}
                                        className={[
                                            'w-full rounded-lg px-3 py-2.5 text-left transition disabled:cursor-not-allowed',
                                            isSelected
                                                ? 'bg-blue-50 dark:bg-blue-950/40'
                                                : 'hover:bg-slate-100 dark:hover:bg-slate-900',
                                        ].join(' ')}
                                    >
                                        <p className="truncate text-sm font-medium text-slate-900 dark:text-slate-100">
                                            {chat.title}
                                        </p>

                                        <div className="mt-1 flex items-center gap-2 text-xs text-slate-500">
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
                                                    <span>•</span>
                                                    <span>Pinned</span>
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


            {/* Conversation */}
            <main className="flex min-w-0 flex-1 flex-col">

                {selectedChat ? (
                    <>
                        {/* Header */}
                        <header className="border-b border-slate-200 px-6 py-4 dark:border-slate-800">

                            <div className="flex items-center justify-between gap-4">

                                <div className="min-w-0">
                                    <h1 className="truncate text-lg font-semibold text-slate-900 dark:text-white">
                                        {selectedChat.title}
                                    </h1>

                                    <div className="mt-1 flex items-center gap-2 text-sm text-slate-500">

                                        <span>
                                            {selectedChat.study_mode}
                                        </span>

                                        {selectedChat.subject && (
                                            <>
                                                <span>•</span>

                                                <span>
                                                    {selectedChat.subject}
                                                </span>
                                            </>
                                        )}

                                    </div>
                                </div>


                                {selectedChat.is_pinned && (
                                    <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 dark:bg-blue-950 dark:text-blue-300">
                                        Pinned
                                    </span>
                                )}

                            </div>

                        </header>


                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-6">

                            {isLoadingMessages ? (
                                <div className="flex h-full items-center justify-center">
                                    <p className="text-sm text-slate-500">
                                        Loading conversation...
                                    </p>
                                </div>
                            ) : messages.length === 0 ? (
                                <div className="flex h-full items-center justify-center">

                                    <div className="max-w-md text-center">

                                        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                                            What would you like to study?
                                        </h2>

                                        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                                            Ask MedEase AI a medical question to start this conversation.
                                        </p>

                                    </div>

                                </div>
                            ) : (
                                <div className="mx-auto max-w-3xl space-y-5">

                                    {messages.map((message) => {
                                        if (message.role === 'system') {
                                            return null
                                        }

                                        const isUser =
                                            message.role === 'user'

                                        return (
                                            <div
                                                key={message.id}
                                                className={[
                                                    'flex',
                                                    isUser
                                                        ? 'justify-end'
                                                        : 'justify-start',
                                                ].join(' ')}
                                            >
                                                <div
                                                    className={[
                                                        'max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6',
                                                        isUser
                                                            ? 'bg-blue-600 text-white'
                                                            : 'bg-slate-100 text-slate-900 dark:bg-slate-900 dark:text-slate-100',
                                                    ].join(' ')}
                                                >
                                                    {message.content}
                                                </div>
                                            </div>
                                        )
                                    })}


                                    {isSending && (
                                        <div className="flex justify-start">

                                            <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                                                MedEase AI is thinking...
                                            </div>

                                        </div>
                                    )}


                                    <div ref={messagesEndRef} />

                                </div>
                            )}

                        </div>


                        {/* Error */}
                        {error && (
                            <div className="border-t border-red-200 bg-red-50 px-6 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
                                {error}
                            </div>
                        )}


                        {/* Message input */}
                        <div className="border-t border-slate-200 p-4 dark:border-slate-800">

                            <form
                                onSubmit={handleSendMessage}
                                className="mx-auto flex max-w-3xl items-end gap-3"
                            >

                                <textarea
                                    value={messageInput}
                                    disabled={isSending}
                                    rows={1}
                                    placeholder="Ask a medical question..."
                                    onChange={(event) => {
                                        setMessageInput(event.target.value)
                                    }}
                                    onKeyDown={(event) => {
                                        if (
                                            event.key === 'Enter' &&
                                            !event.shiftKey
                                        ) {
                                            event.preventDefault()

                                            event.currentTarget.form?.requestSubmit()
                                        }
                                    }}
                                    className="max-h-40 min-h-11 flex-1 resize-none rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                                />

                                <button
                                    type="submit"
                                    disabled={
                                        isSending ||
                                        !messageInput.trim()
                                    }
                                    className="h-11 rounded-xl bg-blue-600 px-5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {isSending
                                        ? 'Sending...'
                                        : 'Send'}
                                </button>

                            </form>


                            <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-slate-400">
                                Enter to send • Shift + Enter for a new line
                            </p>

                        </div>
                    </>
                ) : (
                    /* No chat selected */
                    <div className="flex flex-1 items-center justify-center p-6">

                        <div className="max-w-xl text-center">

                            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                                MedEase AI Tutor
                            </h1>

                            <p className="mt-3 text-slate-500 dark:text-slate-400">
                                Choose a previous conversation or start a new chat to begin studying.
                            </p>

                        </div>

                    </div>
                )}


                {!selectedChat && error && (
                    <div className="border-t border-red-200 bg-red-50 px-6 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
                        {error}
                    </div>
                )}

            </main>
        </div>
    )
}