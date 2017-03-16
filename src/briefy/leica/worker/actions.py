"""Briefy Leica worker."""
from briefy.common.users import SystemUser
from briefy.leica.log import worker_logger as logger
from briefy.leica.models import Assignment
from briefy.leica.models import Comment

import transaction


def validate_assignment(laure_data: object, session: object) -> (bool, dict):
    """Perform necessary transition after photo set validation.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was sucessful, empty dict
    """
    with transaction.manager:
        assignment_id = laure_data.assignment.id
        assignment = Assignment.get(assignment_id)

        if not assignment:
            logger.error('''Got message with unexisting assignment id {0}'''.format(assignment_id))
            return False, {}

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
        assignment.workflow.context = SystemUser
        assignment.workflow.validate_assets(
                message='Validated submission.'
            )
        logger.info('''Assignment {0} state set to {1}'''.format(assignment.slug, assignment.state))

    return True, {}


def ignored_assignment(laure_data: object, session: object) -> (bool, dict):
    """Perform necessary transition after photo set validation.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was sucessful, empty dict
    """
    with transaction.manager:
        assignment_id = laure_data.assignment.id
        assignment = Assignment.get(assignment_id)

        if not assignment:
            logger.error('''Got message for unknown assignment id {0}'''.format(assignment_id))
            return False, {}

        if assignment.state != 'asset_validation':
            logger.error(
                '''Got message to transition assignment '{0}' which is in state '{1}' '''.format(
                    assignment_id,
                    assignment.state
                )
            )
            return False, {}

        logger.info(
            '''Assignment '{0}' assets validation ignored. Transitioning to 'in_qa' '''.format(
                assignment_id
            )
        )
        assignment.workflow.context = SystemUser
        assignment.workflow.validate_assets(
                message='Ignored validation.'
            )
        logger.info('''Assignment {0} state set to {1}'''.format(assignment.slug, assignment.state))

    return True, {}


def invalidate_assignment(laure_data: object, session: object) -> (bool, dict):
    """Perform necessary transition and field update after photo set was deemed invalid.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was successful, empty dict
    """
    with transaction.manager:
        assignment_id = laure_data.assignment.id
        assignment = Assignment.get(assignment_id)

        if not assignment:
            logger.error('''Got message with unexisting assignment id {0}'''.format(assignment_id))
            return False, {}

        if assignment.state != 'asset_validation':
            logger.error('''Got message to invalidate '{0}' which is in state '{1}' '''.format(
                assignment_id,
                assignment.state
            ))
            return False, {}

        feedback_text = '{0}'.format(
            laure_data.validation.complete_feedback
        )

        logger.info(
            '''Assignment '{0}' assets reported as not sufficient. Transitioning back '''
            ''' to 'waiting_assets' and adding comments to assignment.'''.format(
                assignment_id
            )
        )

        assignment.workflow_context = SystemUser

        assignment.workflow.invalidate_assets(
            message=feedback_text
        )
        logger.info('''Assignment {0} state set to {1}'''.format(assignment.slug, assignment.state))

        return True, {}


def approve_assignment(
    laure_data: object,
    session: object,
    copy_ignored: bool=False
) -> (bool, dict):
    """Perform necessary updates after set was copied to destination folders.

    :param laure_data: Python object representing Laure data after assignment approval
    :param copy_ignored: Set when copying assets was ignored on ms.laure
    :return: Flag indicating wether operation was successfull, empty dict
    """
    with transaction.manager:
        assignment_id = laure_data.guid
        assignment = Assignment.get(assignment_id)
        if not assignment:
            logger.warn('Got assignment approval message for non existing assignment {0}'.format(
                assignment_id))
            return False, {}

        order = assignment.order
        delivery_info = order.delivery.copy() if order.delivery else {}
        if not copy_ignored:
            # Ensure the correct key is updated and object is set as dirty
            delivery_info['gdrive'] = laure_data.delivery_url
            delivery_info['archive'] = laure_data.archive_url

            # TODO: Unless google drive is phased out soon, this URL should be
            # stored on the model.
            logger.info(
                '''Assets for assignment '{0}' are archived at '{1}' '''.format(
                    assignment_id,
                    delivery_info['archive']
                )
            )

            msg = '''Assets copied over on laure - committing delivery URL to order '{order_id}' '''
        else:
            # We need to get the existing delivery to execute the proper transition
            msg = '''Assets were a result of previous manual review and were not touched on ms.laure. Order '{order_id} ' unchanged!'''  # noQA

        logger.info(
            msg.format(
                order_id=assignment.order.id
            )
        )
        if order.state == 'in_qa':
            fields = dict(delivery=delivery_info)
            wf = order.workflow
            wf.context = SystemUser
            wf.deliver(
                fields=fields,
                message='Assets automatic delivered.'
            )
        elif order.state == 'delivered':
            order.delivery = delivery_info
        else:
            msg = 'Order in incorrect state: {state}'.format(state=order.state)
            logger.error(msg)
            raise Exception(msg)

    return True, {}


def approve_previously_refused_assignment(laure_data: object, session: object,) -> (bool, dict):
    """Change assignment state, without updating folder information.

    Called when copyng assets have been ignored on ms.laure
    :param laure_data: Python object representing Laure data after assignment approval
    :return: Flag indicating wether operation was successfull, empty dict
    """
    return approve_assignment(laure_data, session, copy_ignored=True)


def asset_copy_malfunction(laure_data: object, session: object) -> (bool, dict):
    """Perform necessary transition and field update after photo set was deemed invalid.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was successful, empty dict
    """
    with transaction.manager:
        assignment_id = laure_data.assignment.id
        assignment = Assignment.get(assignment_id)
        if not assignment:
            logger.warn('Got assignment approval message for non existing assignment {0}'.format(
                assignment_id))
            return False, {}

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
            entity_id=assignment_id,
            entity_type=assignment.__class__.__name__,
            author_id=SystemUser.id,
            author_role='system',
            to_role='qa_manager',
            content=text,
            internal=True,
        )
        session.add(comment)

        logger.warn(
            '''There was a problem copying assets to delivery folders.'''
            '''Adding comment to assignment {0}'''.format(assignment_id)
        )

        comment.workflow_context = SystemUser
        assignment.workflow_context = SystemUser
        assignment.comments.append(comment)

    return True, {}
