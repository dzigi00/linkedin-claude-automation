"""
LinkedIn posting tools.
"""
import logging
import traceback
from typing import Any
from fastmcp import Context, FastMCP
from linkedin_mcp_server.config.schema import DEFAULT_TOOL_TIMEOUT_SECONDS
from linkedin_mcp_server.core.exceptions import AuthenticationError
from linkedin_mcp_server.dependencies import get_ready_extractor, handle_auth_error
from linkedin_mcp_server.error_handler import raise_tool_error

logger = logging.getLogger(__name__)

def register_posting_tools(mcp: FastMCP, *, tool_timeout: float = DEFAULT_TOOL_TIMEOUT_SECONDS) -> None:
    @mcp.tool(timeout=tool_timeout, title="Create Post", annotations={"destructiveHint": True, "openWorldHint": True}, tags={"posting", "actions"}, exclude_args=["extractor"])
    async def create_post(text: str, confirm_post: bool, ctx: Context, extractor: Any | None = None) -> dict[str, Any]:
        """Create a new LinkedIn post. confirm_post must be True to publish."""
        try:
            extractor = extractor or await get_ready_extractor(ctx, tool_name="create_post")
            if not confirm_post:
                return {"status": "dry_run", "message": "Set confirm_post=True to publish.", "post_text": text}
            page = extractor._page
            await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            await page.get_by_text("Start a post", exact=True).first.click()
            await page.wait_for_timeout(3000)
            editor = page.locator("div.ql-editor[contenteditable='true']").first
            await editor.wait_for(state="visible", timeout=15000)
            await editor.click()
            await editor.fill(text)
            await page.wait_for_timeout(2000)
            posted = False
            try:
                post_btn = page.get_by_role("button", name="Post", exact=True).last
                await post_btn.wait_for(state="visible", timeout=10000)
                await post_btn.click()
                posted = True
            except Exception:
                pass
            if not posted:
                try:
                    buttons = page.locator("button")
                    count = await buttons.count()
                    for i in range(count):
                        btn = buttons.nth(i)
                        btn_text = await btn.inner_text()
                        if btn_text.strip() == "Post":
                            await btn.click()
                            posted = True
                            break
                except Exception:
                    pass
            if not posted:
                return {"status": "error", "message": "Could not find the Post button."}
            await page.wait_for_timeout(3000)
            return {"status": "published", "message": "Post published successfully.", "post_text": text}
        except AuthenticationError as e:
            try:
                await handle_auth_error(e, ctx)
            except Exception as ex:
                raise_tool_error(ex, "create_post")
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error("create_post failed: %s", error_details)
            return {"status": "error", "message": str(e), "traceback": error_details}

    @mcp.tool(timeout=tool_timeout, title="Comment On Post", annotations={"destructiveHint": True, "openWorldHint": True}, tags={"posting", "actions"}, exclude_args=["extractor"])
    async def comment_on_post(post_url: str, comment_text: str, confirm_comment: bool, ctx: Context, extractor: Any | None = None) -> dict[str, Any]:
        """Comment on a LinkedIn post. confirm_comment must be True to post."""
        try:
            extractor = extractor or await get_ready_extractor(ctx, tool_name="comment_on_post")
            if not confirm_comment:
                return {"status": "dry_run", "message": "Set confirm_comment=True to post.", "comment_text": comment_text}
            page = extractor._page
            await page.goto(post_url, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Step 1: Click the Comment button (has aria-label="Comment", no text)
            await page.locator("button[aria-label='Comment']").first.click()
            await page.wait_for_timeout(2000)

            # Step 2: Type into the comment editor
            editor = page.locator("div.ql-editor[contenteditable='true']").first
            await editor.wait_for(state="visible", timeout=15000)
            await editor.click()
            await editor.fill(comment_text)
            await page.wait_for_timeout(2000)

            # Step 3: Click the submit button (has text "Comment", no aria-label)
            # Find button with innerText "Comment" and no aria-label
            submitted = False
            buttons = page.locator("button")
            count = await buttons.count()
            for i in range(count):
                btn = buttons.nth(i)
                try:
                    btn_text = await btn.inner_text()
                    aria = await btn.get_attribute("aria-label")
                    if btn_text.strip() == "Comment" and aria is None:
                        await btn.click()
                        submitted = True
                        break
                except Exception:
                    continue

            if not submitted:
                return {"status": "error", "message": "Could not find the comment submit button."}

            await page.wait_for_timeout(2000)
            return {"status": "commented", "message": "Comment posted successfully.", "comment_text": comment_text, "post_url": post_url}

        except AuthenticationError as e:
            try:
                await handle_auth_error(e, ctx)
            except Exception as ex:
                raise_tool_error(ex, "comment_on_post")
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error("comment_on_post failed: %s", error_details)
            return {"status": "error", "message": str(e), "traceback": error_details}