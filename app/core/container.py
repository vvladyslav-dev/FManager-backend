from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.form_repository import FormRepository
from app.infrastructure.repositories.form_submission_repository import FormSubmissionRepository
from app.infrastructure.repositories.file_repository import FileRepository
from app.application.handlers.auth.register_handler import RegisterHandler
from app.application.handlers.auth.login_handler import LoginHandler
from app.application.handlers.forms.create_form_handler import CreateFormHandler
from app.application.handlers.forms.get_form_handler import GetFormHandler
from app.application.handlers.forms.get_forms_by_creator_handler import GetFormsByCreatorHandler
from app.application.handlers.forms.update_form_handler import UpdateFormHandler
from app.application.handlers.forms.delete_form_handler import DeleteFormHandler
from app.application.handlers.submissions.submit_form_handler import SubmitFormHandler
from app.application.handlers.submissions.get_submissions_by_admin_handler import GetSubmissionsByAdminHandler
from app.application.handlers.submissions.get_submissions_by_form_handler import GetSubmissionsByFormHandler
from app.application.handlers.submissions.delete_submission_handler import DeleteSubmissionHandler
from app.application.handlers.users.create_user_handler import CreateUserHandler
from app.application.handlers.users.get_user_handler import GetUserHandler
from app.application.handlers.users.list_users_by_admin_handler import ListUsersByAdminHandler
from app.application.handlers.users.update_user_handler import UpdateUserHandler
from app.application.handlers.users.delete_user_handler import DeleteUserHandler
from app.application.handlers.users.get_unapproved_admins_handler import GetUnapprovedAdminsHandler
from app.application.handlers.users.approve_admin_handler import ApproveAdminHandler
from app.application.handlers.users.reject_admin_handler import RejectAdminHandler


class Container(containers.DeclarativeContainer):
    """Dependency Injection Container"""
    
    # Database session provider - will be injected from FastAPI Depends
    db_session = providers.Dependency(instance_of=AsyncSession)
    
    # Repository providers
    user_repository = providers.Factory(
        UserRepository,
        session=db_session
    )
    
    form_repository = providers.Factory(
        FormRepository,
        session=db_session
    )
    
    form_submission_repository = providers.Factory(
        FormSubmissionRepository,
        session=db_session
    )
    
    file_repository = providers.Factory(
        FileRepository,
        session=db_session
    )
    
    # Handler providers
    create_form_handler = providers.Factory(
        CreateFormHandler,
        form_repository=form_repository
    )
    
    get_form_handler = providers.Factory(
        GetFormHandler,
        form_repository=form_repository
    )
    
    submit_form_handler = providers.Factory(
        SubmitFormHandler,
        user_repository=user_repository,
        form_repository=form_repository,
        submission_repository=form_submission_repository,
        file_repository=file_repository,
        session=db_session
    )
    
    get_submissions_by_admin_handler = providers.Factory(
        GetSubmissionsByAdminHandler,
        submission_repository=form_submission_repository
    )
    
    get_submissions_by_form_handler = providers.Factory(
        GetSubmissionsByFormHandler,
        submission_repository=form_submission_repository
    )
    
    delete_submission_handler = providers.Factory(
        DeleteSubmissionHandler,
        submission_repository=form_submission_repository
    )
    
    get_forms_by_creator_handler = providers.Factory(
        GetFormsByCreatorHandler,
        form_repository=form_repository
    )
    
    update_form_handler = providers.Factory(
        UpdateFormHandler,
        form_repository=form_repository
    )
    
    delete_form_handler = providers.Factory(
        DeleteFormHandler,
        form_repository=form_repository
    )
    
    create_user_handler = providers.Factory(
        CreateUserHandler,
        user_repository=user_repository
    )
    
    get_user_handler = providers.Factory(
        GetUserHandler,
        user_repository=user_repository
    )
    
    list_users_by_admin_handler = providers.Factory(
        ListUsersByAdminHandler,
        user_repository=user_repository
    )
    
    update_user_handler = providers.Factory(
        UpdateUserHandler,
        user_repository=user_repository
    )
    
    delete_user_handler = providers.Factory(
        DeleteUserHandler,
        user_repository=user_repository
    )
    
    register_handler = providers.Factory(
        RegisterHandler,
        user_repository=user_repository
    )
    
    login_handler = providers.Factory(
        LoginHandler,
        user_repository=user_repository
    )
    
    get_unapproved_admins_handler = providers.Factory(
        GetUnapprovedAdminsHandler,
        user_repository=user_repository
    )
    
    approve_admin_handler = providers.Factory(
        ApproveAdminHandler,
        user_repository=user_repository
    )
    
    reject_admin_handler = providers.Factory(
        RejectAdminHandler,
        user_repository=user_repository
    )


def create_container_with_session(session: AsyncSession) -> Container:
    """Create a new container instance with a specific session"""
    cont = Container()
    cont.db_session.override(session)
    return cont


# Global container instance (for cases where session is provided via override)
container = Container()


