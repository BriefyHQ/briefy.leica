"""Briefy Leica worker."""
from briefy.common.users import SystemUser
from briefy.leica.cache import cache_region
from briefy.leica.log import worker_logger as logger
from briefy.leica.models import Assignment
from briefy.leica.models import Comment
from briefy.leica.models import Order

import transaction


def update_delivery(order: Order, laure_data: object) -> dict:
    """Update the delivery information of an order using event data.

    :param order: instance of Order model
    :return: true if delivery was updated
    """
    delivery_info = order.delivery if order.delivery else {}
    delivery_url = laure_data._get('delivery_url', None)
    if delivery_url:
        delivery_info['gdrive'] = laure_data.delivery_url
    archive_url = laure_data._get('archive_url', None)
    if archive_url:
        delivery_info['archive'] = laure_data.archive_url

    if delivery_info and delivery_info != order.delivery:
        logger.info(
            '''Delivery will be update for assignment '{0}' Delivery: '{1}' '''.format(
                laure_data.guid,
                delivery_info
            )
        )
        order.delivery = delivery_info

    return delivery_info


def validate_assignment(laure_data: object, session: object) -> (bool, dict):
    """Perform necessary transition after photo set validation.

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

        cache_region.invalidate(assignment)

    return True, {}


def ignored_assignment(laure_data: object, session: object) -> (bool, dict):
    """Perform necessary transition after photo set validation.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating whether operation was successful, empty dict
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

        cache_region.invalidate(assignment)

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
    :return: Flag indicating if the operation was successful, empty dict
    """
    status = False
    with transaction.manager:
        assignment_id = laure_data.assignment.id
        assignment = Assignment.get(assignment_id)
        if not assignment:
            logger.warn('Got assignment approval message for non existing assignment {0}'.format(
                assignment_id))
            return False, {}

        order = assignment.order
        if not copy_ignored:
            delivery_info = update_delivery(order, laure_data)
            msg = '''Assets copied over on laure - committing delivery URL to order '{order_id}' '''
            status = True
        else:
            # We need to get the existing delivery to execute the proper transition
            msg = '''Assets were a result of previous manual review and were not touched on ms.laure. Order '{order_id} ' unchanged!'''  # noQA
            status = True
            delivery_info = order.delivery

        if order.state == 'in_qa' and assignment.state == 'approved':
            # force new instance object to make sure sqlalchemy will detect the change
            delivery = delivery_info.copy()
            fields = dict(delivery=delivery)
            wf = order.workflow
            wf.context = SystemUser
            wf.deliver(
                fields=fields,
                message='Assets automatic delivered.'
            )

        cache_region.invalidate(assignment)
        cache_region.invalidate(order)

        logger.info(
            msg.format(
                order_id=assignment.order.id
            )
        )

    return status, {}


def approve_previously_refused_assignment(laure_data: object, session: object,) -> (bool, dict):
    """Change assignment state, without updating folder information.

    Called when copying assets have been ignored on ms.laure
    :param laure_data: Python object representing Laure data after assignment approval
    :return: Flag indicating if the operation was successfull, empty dict
    """
    return approve_assignment(laure_data, session, copy_ignored=True)


def asset_copy_malfunction(laure_data: object, session: object) -> (bool, dict):
    """Perform necessary transition and field update after photo set was deemed invalid.

    :param laure_data: Python object representing Laure data after assignment validation
    :return: Flag indicating if the operation was successful, empty dict
    """
    with transaction.manager:
        assignment_id = laure_data.assignment.id
        assignment = Assignment.get(assignment_id)
        if not assignment:
            logger.warn('Got assignment message for non existing assignment {0}'.format(
                assignment_id))
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
            '''There was a problem copying assets to delivery or archive folders.'''
            '''Adding comment to assignment {0}'''.format(assignment_id)
        )

        comment.workflow_context = SystemUser
        assignment.workflow_context = SystemUser
        assignment.comments.append(comment)

        cache_region.invalidate(assignment)

    return True, {}
