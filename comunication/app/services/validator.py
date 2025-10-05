"""
External UKNF Validator Service Client
Handles communication with external validation service
"""
import httpx
from typing import Optional, Dict, Any


class ValidatorClient:
    """
    Client for external UKNF validation service
    
    This is a thin interface that submits files for validation
    and expects async webhook callbacks to /validators/uknf/callback
    """
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize validator client
        
        Args:
            base_url: Base URL of external validator service
            api_key: API key for authentication
        """
        self.base_url = base_url or "https://validator.uknf.gov.pl/api/v1"
        self.api_key = api_key
        self.timeout = 30.0
    
    async def submit_validation(
        self,
        file_url: str,
        report_file_id: int,
        metadata: Dict[str, Any],
        callback_url: str
    ) -> Optional[str]:
        """
        Submit a file for validation
        
        Args:
            file_url: URL to the file to validate
            report_file_id: Internal report file ID
            metadata: Additional metadata (UKNF ID, subject name, period, etc.)
            callback_url: Webhook URL for results
            
        Returns:
            external_job_id: Unique job ID from validator, or None on error
        """
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "file_url": file_url,
            "reference_id": str(report_file_id),
            "metadata": metadata,
            "callback_url": callback_url
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/validate",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 202:
                    result = response.json()
                    return result.get("job_id")
                else:
                    # Log error
                    print(f"Validator submission failed: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.RequestError as e:
            print(f"Validator request error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error submitting to validator: {str(e)}")
            return None
    
    def get_status_meaning(self, status_code: str) -> str:
        """
        Get human-readable explanation of status code
        
        Args:
            status_code: Status code from REPORT_STATUS_DICT
            
        Returns:
            Human-readable explanation
        """
        meanings = {
            'DRAFT': 'Raport jest w fazie roboczej. Plik został dodany ale walidacja jeszcze nie została uruchomiona.',
            'SUBMITTED': 'Raport został przekazany do systemu walidacji. Nadano unikalny identyfikator i rozpoczęto proces weryfikacji.',
            'IN_PROGRESS': 'Walidacja jest w trakcie realizacji. Trwa sprawdzanie danych według reguł biznesowych.',
            'SUCCESS': 'Proces walidacji zakończył się sukcesem! Nie wykryto żadnych błędów. Dane zostały przekazane do systemu analitycznego.',
            'RULE_ERRORS': 'Wykryto błędy walidacji zgodnie z regułami biznesowymi. Sprawdź szczegóły błędów i prześlij korektę.',
            'TECH_ERROR': 'Wystąpił błąd techniczny podczas przetwarzania. Skontaktuj się z pomocą techniczną.',
            'TIMEOUT': 'Przekroczono maksymalny czas oczekiwania (24h). Walidacja została przerwana. Proszę przesłać plik ponownie.',
            'QUESTIONED_BY_UKNF': 'Raport został zakwestionowany przez pracownika UKNF. Sprawdź szczegóły i opis nieprawidłowości.'
        }
        return meanings.get(status_code, 'Status nieznany')
    
    def get_next_actions(self, status_code: str, has_errors: bool = False) -> list:
        """
        Get suggested next actions based on status
        
        Args:
            status_code: Current status code
            has_errors: Whether validation errors exist
            
        Returns:
            List of suggested actions
        """
        if status_code == 'DRAFT':
            return ['Rozpocznij walidację przesyłając plik']
        elif status_code == 'SUBMITTED' or status_code == 'IN_PROGRESS':
            return ['Poczekaj na zakończenie walidacji', 'Sprawdź status później']
        elif status_code == 'SUCCESS':
            return ['Raport został zaakceptowany', 'Możesz zamknąć sprawę']
        elif status_code == 'RULE_ERRORS':
            return [
                'Pobierz raport walidacji',
                'Przejrzyj błędy szczegółowo',
                'Popraw dane w pliku źródłowym',
                'Prześlij korektę (wersja 2)'
            ]
        elif status_code == 'TECH_ERROR' or status_code == 'TIMEOUT':
            return [
                'Sprawdź plik źródłowy',
                'Spróbuj przesłać ponownie',
                'Skontaktuj się z pomocą techniczną jeśli problem się powtarza'
            ]
        elif status_code == 'QUESTIONED_BY_UKNF':
            return [
                'Przeczytaj opis nieprawidłowości',
                'Skontaktuj się z odpowiedzialnym pracownikiem UKNF',
                'Przygotuj wyjaśnienia lub korektę'
            ]
        else:
            return ['Sprawdź szczegóły raportu']


# Global validator instance
validator_client = ValidatorClient()

