import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from typing_extensions import Annotated

import ingenious.dependencies as igen_deps
from ingenious.files.files_repository import FileStorage
from ingenious.utils.namespace_utils import discover_workflows, normalize_workflow_name

logger = logging.getLogger(__name__)
router = APIRouter()


class UpdatePromptRequest(BaseModel):
    content: str


@router.get("/revisions/list")
def list_revisions(
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_conditional_security)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    """
    List all available revisions (workflow directories) in the prompt templates.
    """
    try:
        # Get the base templates/prompts path
        base_template_path = asyncio.run(fs.get_prompt_template_path())
        
        # List all directories in the templates/prompts folder
        revisions_raw = asyncio.run(fs.list_files(file_path=base_template_path))
        
        # Filter to find directories (these would be the revision IDs)
        # For Azure Blob Storage, we need to look for folder prefixes
        revision_ids = set()
        for item in revisions_raw:
            # Extract revision ID from the path
            # For Azure, items are full paths like "templates/prompts/submission-over-criteria-v1/file.jinja"
            # For local, items are filenames directly
            if "/" in item:
                path_parts = item.split("/")
                if len(path_parts) >= 4:  # templates/prompts/revision_id/filename
                    revision_ids.add(path_parts[2])
        
        # If no revisions found via path parsing, try to discover from workflows
        if not revision_ids:
            workflows = discover_workflows()
            for workflow in workflows:
                # Check if this workflow has prompts
                workflow_path = asyncio.run(fs.get_prompt_template_path(workflow))
                try:
                    workflow_files = asyncio.run(fs.list_files(file_path=workflow_path))
                    if workflow_files:
                        revision_ids.add(workflow)
                except:
                    pass
        
        return {
            "revisions": sorted(list(revision_ids)),
            "count": len(revision_ids),
            "discovered_from": "template_directories" if revision_ids else "workflows"
        }
    except Exception as e:
        logger.exception(f"Error listing revisions: {e}")
        return {"revisions": [], "count": 0, "error": str(e)}


@router.get("/workflows/list")
def list_workflows_for_prompts(
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_conditional_security)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    """
    List all available workflows that have prompt templates.
    """
    try:
        workflows = discover_workflows()
        workflows_with_prompts = []
        
        for workflow in workflows:
            # Try both underscore and hyphenated formats
            workflow_variants = [workflow]
            if "_" in workflow:
                workflow_variants.append(workflow.replace("_", "-"))
            elif "-" in workflow:
                workflow_variants.append(workflow.replace("-", "_"))
            
            found_prompts = False
            for variant in workflow_variants:
                try:
                    # Check if this workflow has prompts
                    workflow_path = asyncio.run(fs.get_prompt_template_path(variant))
                    workflow_files = asyncio.run(fs.list_files(file_path=workflow_path))
                    if workflow_files:
                        prompt_files = [f for f in workflow_files if f.endswith((".md", ".jinja"))]
                        if prompt_files:
                            workflows_with_prompts.append({
                                "workflow": workflow,
                                "revision_id": variant,
                                "prompt_count": len(prompt_files),
                                "prompt_files": prompt_files
                            })
                            found_prompts = True
                            break
                except Exception as e:
                    logger.debug(f"Error checking workflow {variant}: {e}")
                    continue
            
            # If we couldn't find prompts, still include the workflow
            if not found_prompts:
                workflows_with_prompts.append({
                    "workflow": workflow,
                    "revision_id": workflow,
                    "prompt_count": 0,
                    "prompt_files": [],
                    "note": "No prompts found or path not accessible"
                })
        
        return {
            "workflows": workflows_with_prompts,
            "count": len(workflows_with_prompts),
            "total_workflows_discovered": len(workflows)
        }
    except Exception as e:
        logger.exception(f"Error listing workflows: {e}")
        return {"workflows": [], "count": 0, "error": str(e)}


@router.get("/prompts/list/{revision_id}")
def list_prompts_enhanced(
    revision_id: str,
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_conditional_security)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    """
    Enhanced prompt listing with better metadata and error handling.
    """
    try:
        # Normalize the revision_id to handle both hyphenated and underscored formats
        normalized_revision_id = normalize_workflow_name(revision_id)
        
        # Try both original and normalized revision IDs
        revision_ids_to_try = [revision_id, normalized_revision_id]
        if revision_id != normalized_revision_id:
            revision_ids_to_try.append(revision_id.replace("_", "-"))
        
        files = []
        successful_revision_id = None
        
        for rid in revision_ids_to_try:
            try:
                prompt_template_folder = asyncio.run(fs.get_prompt_template_path(revision_id=rid))
                files_raw = asyncio.run(fs.list_files(file_path=prompt_template_folder))
                
                # Filter to get only template files
                potential_files = []
                for f in files_raw:
                    if f.endswith((".md", ".jinja")):
                        # For Azure Blob Storage, extract just the filename
                        if "/" in f:
                            filename = f.split("/")[-1]
                        else:
                            filename = f
                        potential_files.append(filename)
                
                if potential_files:
                    files = sorted(potential_files)
                    successful_revision_id = rid
                    break
                    
            except Exception as e:
                logger.debug(f"Failed to list prompts for revision {rid}: {e}")
                continue
        
        if not files and not successful_revision_id:
            # Return empty result with helpful information
            return {
                "revision_id": revision_id,
                "normalized_revision_id": normalized_revision_id,
                "files": [],
                "count": 0,
                "attempted_revisions": revision_ids_to_try,
                "note": "No prompt templates found for this revision. Check if the revision exists or if templates have been uploaded."
            }
        
        return {
            "revision_id": revision_id,
            "actual_revision_used": successful_revision_id,
            "normalized_revision_id": normalized_revision_id,
            "files": files,
            "count": len(files),
            "attempted_revisions": revision_ids_to_try
        }
        
    except Exception as e:
        logger.exception(f"Error listing prompts for revision {revision_id}: {e}")
        return {
            "revision_id": revision_id,
            "files": [],
            "count": 0,
            "error": str(e)
        }


@router.get("/prompts/view/{revision_id}/{filename}")
def view(
    revision_id: str,
    filename: str,
    request: Request,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_conditional_security)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    prompt_template_folder = asyncio.run(
        fs.get_prompt_template_path(revision_id=revision_id)
    )
    content = asyncio.run(
        fs.read_file(file_name=filename, file_path=prompt_template_folder)
    )
    return content


@router.post("/prompts/update/{revision_id}/{filename}")
async def update(
    revision_id: str,
    filename: str,
    request: Request,
    update_request: UpdatePromptRequest,
    credentials: Annotated[
        HTTPBasicCredentials, Depends(igen_deps.get_conditional_security)
    ],
    fs: FileStorage = Depends(igen_deps.get_file_storage_revisions),
):
    prompt_template_folder = await fs.get_prompt_template_path(revision_id=revision_id)
    try:
        await fs.write_file(
            contents=update_request.content,
            file_name=filename,
            file_path=prompt_template_folder,
        )
        return {"message": "File updated successfully"}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Failed to update file")
