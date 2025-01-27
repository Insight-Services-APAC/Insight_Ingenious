from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
import asyncio
from pathlib import Path
from ingenious_prompt_tuner.utilities import requires_auth, utils_class, requires_selected_revision, get_selected_revision_direct_call

# Authentication Helpers

bp = Blueprint('prompts', __name__, url_prefix='/prompts')


# Routes

@bp.route('/edit/<filename>', methods=['GET', 'POST'])
@requires_auth
@requires_selected_revision
def edit(filename):
    utils: utils_class = current_app.utils
    prompt_template_folder = asyncio.run(utils.get_prompt_template_folder())
    if request.method == 'POST':
        new_content = request.form.get('file_content', '')
        asyncio.run(utils.fs.write_file(
            contents=new_content,
            file_name=filename,
            file_path=prompt_template_folder
            )
        )
        return redirect(url_for('prompts.list'))
    else:
        content = asyncio.run(utils.fs.read_file(            
            file_name=filename,
            file_path=prompt_template_folder
            )
        )

        return render_template('/prompts/edit_prompt.html', filename=filename, content=content)


@bp.route('/list')
@requires_auth
@requires_selected_revision
def list():
    utils: utils_class = current_app.utils
    prompt_template_folder = asyncio.run(utils.get_prompt_template_folder())
    try:
        files_raw = asyncio.run(
            utils.fs.list_files(
                file_path=prompt_template_folder
                )
            )
        files = sorted([
            Path(f).name for f in files_raw if f.endswith(('.md', '.jinja'))
        ])
    except FileNotFoundError:
        files = []
    return render_template('prompts/view_prompts.html', files=files)
