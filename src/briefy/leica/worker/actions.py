"""Briefy Leica worker."""
from briefy.common.users import SystemUser
from briefy.leica import logger
from briefy.leica.models import Assignment
from briefy.leica.models import Comment

import transaction


def validate_assignment(laure_data: object) -> (bool, dict):
    """Perform necessary transition after photo set validation.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was sucessful, empty dict
    """
    assignment_id = laure_data.assignment_info.id
    assignment = Assignment.query().get(assignment_id)

    if assignment.state != 'asset_validation':
        logger.error(
            '''Got message to validate assignment '{0}' which is in state '{1}' '''.format(
                assignment_id,
                assignment.state
            )
        )
        return False, {}

    logger.info(
        '''Assignment '{0}' assets reported as ok. Transitioning to 'in_qa' '''.format(
            assignment_id
        )
    )
    assignment.workflow_context = SystemUser
    with transaction.manager:
        assignment.workflow.validate_assets(
            message='Validated submission.'
        )

    return True, {}


def invalidate_assignment(laure_data: object) -> (bool, dict):
    """Perform necessary transition and field update after photo set was deemed invalid.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was successful, empty dict
    """
    assignment_id = laure_data.assignment_info.id
    assignment = Assignment.query().get(assignment_id)

    if assignment.state != 'asset_validation':
        logger.error('''Got message to invalidate '{0}' which is in state '{1}' '''.format(
            assignment_id,
            assignment.state
        ))
        return False, {}

    feedback_text = '{0}\n\n{1}'.format(
        laure_data.validation_info.feedback,
        laure_data.validation_info.complete_feedback
    )

    feedback_comment = Comment(
        author_id=SystemUser.id,
        author_role='system',
        to_role='professional',
        content=feedback_text
    )

    logger.info(
        '''Assignment '{0}' assets reported as not sufficient. Transitioning back '''
        ''' to 'waiting_assets' and adding comments to assignment.'''.format(
            assignment_id
        )
    )

    feedback_comment.workflow_context = SystemUser
    assignment.workflow_context = SystemUser
    assignment.comments.append(feedback_comment)
    with transaction.manager:
        assignment.workflow.invalidate_assets(
            message='Invalidated submission.'
        )

    return True, {}


def approve_assignment(laure_data: object) -> (bool, dict):
    """Perform necessary updates after set was copied to destination folders.

    :param laure_data: Python object representing Laure data after assignment approval
    :return: Flag indicating wether operation was successfull, empty dict
    """
    assignment_id = laure_data.assignment_info.id
    assignment = Assignment.query().get(assignment_id)

    # Ensure the correct key is updated and object is set as dirty
    delivery_info = assignment.order.delivery or {}
    delivery_info['gdrive'] = laure_data.delivery_url
    delivery_info['archive'] = laure_data.archive_url

    logger.info(
        '''Assets copied over on laure - committing delivery URL to order '{order_id}' '''.format(
            order_id=assignment.order.id
        )
    )

    with transaction.manager:
        assignment.order.delivery = delivery_info

    # TODO: Unless google drive is phased out soon, this URL should be
    # stored on the model.
    logger.info(
        '''Assets for assignment '{0}' are archived at '{1}' '''.format(
            assignment_id,
            laure_data.archive_url
        )
    )

    return True, {}


def asset_copy_malfunction(laure_data: object) -> (bool, dict):
    """Perform necessary transition and field update after photo set was deemed invalid.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was successful, empty dict
    """
    assignment_id = laure_data.assignment_info.id
    assignment = Assignment.query().get(assignment_id)

    if assignment.state != 'asset_validation':
        logger.error(
            '''Got message to invalidate '{0}' which is in state '{1}' '''.format(
                assignment_id,
                assignment.state
            )
        )
        return False, {}

    text = ('''This assignment's assets could not be copied automatically!\n'''
            '''Please take manual actions that may be needed.''')

    comment = Comment(
        author_id=SystemUser.id,
        author_role='system',
        to_role='qa_manager',
        content=text,
        internal=True,
    )

    logger.warn(
        '''There was a problem copying assets to delivery folders.'''
        '''Adding comment to assignment {0}'''.format(assignment_id)
    )

    comment.workflow_context = SystemUser
    assignment.workflow_context = SystemUser
    with transaction.manager:
        assignment.comments.append(comment)

    return True, {}
