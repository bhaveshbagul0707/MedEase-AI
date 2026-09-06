from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.community import Comment, Post
from app.schemas.common import APIResponse

router = APIRouter(prefix="/community", tags=["Community"])


@router.get("/posts", response_model=APIResponse[list[dict]])
async def list_posts(db: DbSession, current_user: CurrentUser):
    result = await db.execute(select(Post).order_by(Post.created_at.desc()).limit(50))
    return APIResponse(
        message="Posts listed",
        data=[{"id": p.id, "user_id": p.user_id, "title": p.title, "content": p.content,
               "upvote_count": p.upvote_count, "created_at": p.created_at}
              for p in result.scalars().all()],
    )


@router.post("/posts", response_model=APIResponse[dict])
async def create_post(payload: dict, db: DbSession, current_user: CurrentUser):
    title, content = str(payload.get("title", "")).strip(), str(payload.get("content", "")).strip()
    if not title or not content:
        raise HTTPException(status_code=422, detail="Title and content are required")
    post = Post(user_id=current_user.id, title=title, content=content, note_id=payload.get("note_id"))
    db.add(post)
    await db.flush()
    return APIResponse(message="Post created", data={"id": post.id, "title": post.title, "content": post.content})


@router.post("/posts/{post_id}/comments", response_model=APIResponse[dict])
async def create_comment(post_id: int, payload: dict, db: DbSession, current_user: CurrentUser):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    content = str(payload.get("content", "")).strip()
    if not content:
        raise HTTPException(status_code=422, detail="Comment content is required")
    comment = Comment(post_id=post_id, user_id=current_user.id, content=content)
    db.add(comment)
    await db.flush()
    return APIResponse(message="Comment created", data={"id": comment.id, "content": content})
