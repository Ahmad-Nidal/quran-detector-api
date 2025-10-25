from fastapi import APIRouter
from quran_detector import matcher

from app.v1.models.ayah_match import AyahMatch
from app.v1.models.operations_request import OperationsRequest
from app.v1.models.operations_response import OperationsResponse

router = APIRouter()

@router.post("/operations", response_model=OperationsResponse, tags=["Operations"])
async def operations(request: OperationsRequest) -> OperationsResponse:
    """Process Arabic text to detect Quranic verses and/or add annotations."""
    annotater = matcher.qMatcherAnnotater()

    # TODO: handle configuration options from request

    # Both detect and annotate requested
    if "detect" in request.tasks and "annotate" in request.tasks:
        annotated_text, matches = annotater.match_and_annotate(request.text)
        return OperationsResponse(
            annotated_text=annotated_text,
            matches=[
                AyahMatch(
                    surah_name=match["aya_name"],
                    surah_number=0,  # TODO: ?
                    ayah_start=match["aya_start"],
                    ayah_end=match["aya_end"],
                    ayah_text=match["verses"],
                    corrections=[],  # TODO: ?
                    start_index=match["startInText"],
                    end_index=match["endInText"],
                )
                for match in matches
            ]
            if matches
            else None,
        )

    # Only detect requested
    if "detect" in request.tasks:
        matches = annotater.matchAll(request.text)
        return OperationsResponse(
            annotated_text=None,
            matches=[
                AyahMatch(
                    surah_name=match["aya_name"],
                    surah_number=0,  # TODO: ?
                    ayah_start=match["aya_start"],
                    ayah_end=match["aya_end"],
                    ayah_text=match["verses"],
                    corrections=[],  # TODO: ?
                    start_index=match["startInText"],
                    end_index=match["endInText"],
                )
                for match in matches
            ]
            if matches
            else None
        )

    # Only annotate requested
    if "annotate" in request.tasks:
        annotated_text = annotater.annotateTxt(request.text)
        return OperationsResponse(annotated_text=annotated_text, matches=None)

    # Return empty response if no tasks matched
    return OperationsResponse(annotated_text=None, matches=None)
